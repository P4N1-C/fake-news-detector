"""
Database utilities for the Fake News Detector
Contains functions for claim history management using ChromaDB
"""

import logging
import hashlib
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_claim_id(claim_text: str) -> str:
    """
    Generate a unique ID for the claim using MD5 hash
    
    Args:
        claim_text (str): The original news claim text
    
    Returns:
        str: MD5 hash of the lowercased, stripped claim text
    """
    try:
        # Normalize the claim text: lowercase and strip whitespace
        normalized_claim = claim_text.lower().strip()
        
        # Generate MD5 hash
        claim_id = hashlib.md5(normalized_claim.encode('utf-8')).hexdigest()
        
        logger.debug(f"Generated claim ID: {claim_id} for claim: {claim_text[:50]}...")
        return claim_id
        
    except Exception as e:
        logger.error(f"Error generating claim ID for '{claim_text[:50]}...': {str(e)}")
        # Fallback to a simple hash if MD5 fails
        return str(hash(claim_text.lower().strip()))

def is_cached_data_too_old(timestamp_str: str, dependency_duration_days: int) -> bool:
    """
    Check if cached data is too old based on time dependency duration
    
    Args:
        timestamp_str (str): Timestamp string from cached data
        dependency_duration_days (int): Number of days the data remains relevant
    
    Returns:
        bool: True if data is too old, False if still valid
    """
    try:
        if not timestamp_str or dependency_duration_days <= 0:
            return False
        
        # Parse the timestamp
        cached_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        current_time = datetime.now()
        
        # Calculate age of cached data
        age_in_days = (current_time - cached_time).days
        
        logger.debug(f"Cached data age: {age_in_days} days, dependency duration: {dependency_duration_days} days")
        
        return age_in_days > dependency_duration_days
        
    except Exception as e:
        logger.error(f"Error checking cached data age: {str(e)}")
        return False  # Default to using cached data if we can't determine age

async def check_claim_history(claim_text: str, claims_collection, similarity_threshold: float = 0.8, time_dependency_info: dict = None) -> Optional[Dict[str, Any]]:
    """
    Check if a similar claim exists in the claim history database using semantic similarity search
    Now includes time dependency logic: if claim is time-dependent and cached data is too old, proceed with new analysis
    Also includes feedback-based logic: if previous feedback was "inaccurate", proceed with new analysis
    
    Args:
        claim_text (str): The news claim text to check
        claims_collection: ChromaDB collection instance
        similarity_threshold (float): Minimum similarity score (0.0-1.0) to consider a match (default: 0.8)
        time_dependency_info (dict): Time dependency information containing is_time_dependent and dependency_duration_days
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing claim data if found and valid (not too old, good feedback), None otherwise
    """
    try:
        logger.info(f"Checking claim history for: {claim_text[:100]}...")
        
        # Check if ChromaDB collection is available
        if not claims_collection:
            logger.warning("ChromaDB collection not available, skipping history check")
            return None
        
        # Check if collection has any entries
        collection_count = claims_collection.count()
        if collection_count == 0:
            logger.info("Claims collection is empty, no history to check")
            return None
        
        logger.info(f"Searching {collection_count} entries for similar claims with threshold {similarity_threshold}")
        
        # Use semantic similarity search to get multiple similar results for feedback analysis
        try:
            # Query the collection for similar claims using embeddings - get more results to analyze feedback
            query_result = claims_collection.query(
                query_texts=[claim_text],
                n_results=min(5, collection_count),  # Get up to 5 most similar results for feedback analysis
                include=["metadatas", "documents", "distances"]
            )
            
            logger.debug(f"ChromaDB similarity search result: {query_result}")
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB collection for similarity: {str(e)}")
            return None
        
        # Check if any results were found
        if not query_result or not query_result.get("ids") or len(query_result["ids"][0]) == 0:
            logger.info("No similar claims found in history")
            return None
        
        # Analyze all similar results to find the best one based on feedback priority and time dependency
        similar_claims = []
        
        for i in range(len(query_result["ids"][0])):
            similarity_distance = query_result["distances"][0][i]
            similarity_score = 1.0 - similarity_distance  # Convert distance to similarity score
            
            # Check if similarity score meets the threshold
            if similarity_score < similarity_threshold:
                logger.debug(f"Similarity score {similarity_score:.3f} below threshold {similarity_threshold}, skipping")
                continue
            
            # Extract data from this similar result
            try:
                claim_id = query_result["ids"][0][i]
                document = query_result["documents"][0][i] if query_result["documents"] else claim_text
                metadata = query_result["metadatas"][0][i] if query_result["metadatas"] else {}
                
                # Extract feedback information
                user_feedback = metadata.get("user_feedback", None)
                timestamp = metadata.get("timestamp", "Unknown")
                
                # Check time dependency if provided
                is_too_old = False
                if time_dependency_info and time_dependency_info.get("is_time_dependent", False):
                    dependency_duration = time_dependency_info.get("dependency_duration_days", 0)
                    is_too_old = is_cached_data_too_old(timestamp, dependency_duration)
                    logger.debug(f"Time dependency check - Is time dependent: True, Duration: {dependency_duration} days, Is too old: {is_too_old}")
                
                # Parse source_links JSON string back to list
                try:
                    source_links_str = metadata.get("source_links", "[]")
                    if source_links_str:
                        source_links = json.loads(source_links_str)
                    else:
                        source_links = []
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Error parsing source_links JSON: {str(e)}, using empty list")
                    source_links = []
                
                similar_claim_data = {
                    "claim_text": document,
                    "verdict": metadata.get("verdict", "Unknown"),
                    "explanation": metadata.get("explanation", "No explanation available"),
                    "timestamp": timestamp,
                    "source_links": source_links,
                    "claim_id": claim_id,
                    "similarity_score": similarity_score,
                    "user_feedback": user_feedback,
                    "is_too_old": is_too_old
                }
                
                similar_claims.append(similar_claim_data)
                logger.debug(f"Found similar claim - Similarity: {similarity_score:.3f}, Feedback: {user_feedback}, Too old: {is_too_old}")
                
            except (IndexError, KeyError) as e:
                logger.error(f"Error extracting data from similarity search result {i}: {str(e)}")
                continue
        
        if not similar_claims:
            logger.info("No similar claims found above similarity threshold")
            return None
        
        # Apply feedback priority logic: inaccurate > accurate > no feedback
        # But exclude claims that are too old regardless of feedback
        # Sort similar claims by feedback priority and similarity score
        def get_feedback_priority(claim):
            # If claim is too old, give it lowest priority
            if claim.get("is_too_old", False):
                return 0
            
            feedback = claim.get("user_feedback")
            if feedback == "inaccurate":
                return 3  # Highest priority - prioritize updating inaccurate claims
            elif feedback == "accurate":
                return 2  # Medium priority
            elif feedback is None:
                return 1  # Lowest priority (no feedback)
            else:
                return 1  # Default to lowest priority for unknown feedback
        
        # Sort by feedback priority (descending) and then by similarity score (descending)
        similar_claims.sort(key=lambda x: (get_feedback_priority(x), x["similarity_score"]), reverse=True)
        
        # Get the best claim based on feedback priority and time dependency
        best_claim = similar_claims[0]
        best_feedback = best_claim.get("user_feedback")
        is_too_old = best_claim.get("is_too_old", False)
        
        logger.info(f"Best similar claim found - Similarity: {best_claim['similarity_score']:.3f}, Feedback: {best_feedback}, Too old: {is_too_old}")
        
        # Decision logic based on feedback and time dependency
        if is_too_old:
            logger.info(f"Best matching claim is too old for time-dependent analysis - proceeding with new analysis")
            return None  # This will trigger new web search and analysis
        elif best_feedback == "inaccurate":
            logger.info(f"Best matching claim has 'inaccurate' feedback - proceeding with new analysis instead of using cached result")
            return None  # This will trigger new web search and analysis
        elif best_feedback == "accurate" or best_feedback is None:
            # Return the cached result for accurate feedback or no feedback (and not too old)
            logger.info(f"Using cached result - Verdict: {best_claim['verdict']}, Similarity: {best_claim['similarity_score']:.3f}, Feedback: {best_feedback}")
            return best_claim
        else:
            # Unknown feedback type, default to using cached result (if not too old)
            logger.info(f"Unknown feedback type '{best_feedback}', defaulting to cached result")
            return best_claim
            
    except Exception as e:
        logger.error(f"Unexpected error during claim history similarity check for '{claim_text[:50]}...': {str(e)}")
        return None

async def update_claim_history(claim_text: str, verdict: str, explanation: str, claims_collection, search_results: list = None, time_dependency_info: dict = None) -> bool:
    """
    Update claim history database with new analysis results
    
    Args:
        claim_text (str): The original news claim text
        verdict (str): The verdict from LLM analysis
        explanation (str): The explanation from LLM analysis
        claims_collection: ChromaDB collection instance
        search_results (list): List of search results with source URLs (optional)
        time_dependency_info (dict): Time dependency information containing is_time_dependent and dependency_duration_days
    
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        logger.info(f"Updating claim history for: {claim_text[:100]}...")
        
        # Check if ChromaDB collection is available
        if not claims_collection:
            logger.warning("ChromaDB collection not available, skipping history update")
            return False
        
        # Validate claim text is not empty or whitespace-only
        if not claim_text or not claim_text.strip():
            logger.warning("Empty or whitespace-only claim text provided, skipping history update")
            return False
        
        # Generate unique ID for the claim
        claim_id = generate_claim_id(claim_text)
        logger.info(f"Generated claim ID for history update: {claim_id}")
        
        # Create metadata dictionary with verdict, explanation, current UTC timestamp, and source links
        current_timestamp = datetime.utcnow().isoformat()
        metadata = {
            "verdict": verdict,
            "explanation": explanation,
            "timestamp": current_timestamp
        }
        
        # Add time dependency information if provided
        if time_dependency_info:
            metadata["is_time_dependent"] = time_dependency_info.get("is_time_dependent", False)
            metadata["dependency_duration_days"] = time_dependency_info.get("dependency_duration_days", 0)
            logger.debug(f"Added time dependency info: is_time_dependent={metadata['is_time_dependent']}, duration={metadata['dependency_duration_days']} days")
        
        # Add source links if search results are provided
        if search_results and isinstance(search_results, list):
            source_links = []
            for result in search_results:
                if isinstance(result, dict) and result.get("url") and result.get("url") != "No URL available":
                    source_info = {
                        "title": result.get("title", "No title"),
                        "url": result.get("url"),
                        "source": result.get("source", "Unknown"),
                        "snippet": result.get("snippet", "No content available")
                    }
                    source_links.append(source_info)
            
            if source_links:
                metadata["source_links"] = json.dumps(source_links)
                logger.info(f"Added {len(source_links)} source links to claim metadata")
            else:
                logger.info("No valid source links found in search results")
        else:
            logger.info("No search results provided, storing claim without source links")
        
        logger.debug(f"Prepared metadata for claim {claim_id}: verdict={verdict}, timestamp={current_timestamp}, source_links={len(metadata.get('source_links', []))}")
        
        # Use upsert method to add or update the claim in the collection
        try:
            claims_collection.upsert(
                ids=[claim_id],
                documents=[claim_text],
                metadatas=[metadata]
            )
            
            logger.info(f"Successfully upserted claim to database - ID: {claim_id}, Verdict: {verdict}")
            
            # Verify the update by checking collection count
            collection_count = claims_collection.count()
            logger.info(f"Claims collection now contains {collection_count} entries")
            
            return True
            
        except Exception as e:
            logger.error(f"Error upserting claim to ChromaDB collection: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Unexpected error during claim history update for '{claim_text[:50]}...': {str(e)}")
        return False 