"""
Database utilities for the Fake News Detector
Contains functions for claim history management using ChromaDB
"""

import logging
import hashlib
import os
from typing import Optional, Dict, Any
from datetime import datetime

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

async def check_claim_history(claim_text: str, claims_collection) -> Optional[Dict[str, Any]]:
    """
    Check if a claim exists in the claim history database
    
    Args:
        claim_text (str): The news claim text to check
        claims_collection: ChromaDB collection instance
    
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing claim data if found, None if not found
    """
    try:
        logger.info(f"Checking claim history for: {claim_text[:100]}...")
        
        # Check if ChromaDB collection is available
        if not claims_collection:
            logger.warning("ChromaDB collection not available, skipping history check")
            return None
        
        # Generate unique ID for the claim
        claim_id = generate_claim_id(claim_text)
        logger.info(f"Generated claim ID for history check: {claim_id}")
        
        # Query the claims_history collection using the ID
        try:
            query_result = claims_collection.get(
                ids=[claim_id],
                include=["metadatas", "documents"]
            )
            
            logger.debug(f"ChromaDB query result: {query_result}")
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB collection: {str(e)}")
            return None
        
        # Check if any entry was found
        if not query_result or not query_result.get("ids") or len(query_result["ids"]) == 0:
            logger.info(f"No existing entry found for claim ID: {claim_id}")
            return None
        
        # Extract data from the query result
        try:
            # Get the first (and should be only) result
            document = query_result["documents"][0] if query_result["documents"] else claim_text
            metadata = query_result["metadatas"][0] if query_result["metadatas"] else {}
            
            # Extract relevant data from metadata
            stored_data = {
                "claim_text": document,
                "verdict": metadata.get("verdict", "Unknown"),
                "explanation": metadata.get("explanation", "No explanation available"),
                "timestamp": metadata.get("timestamp", "Unknown"),
                "claim_id": claim_id
            }
            
            logger.info(f"Found existing claim in history - Verdict: {stored_data['verdict']}, Timestamp: {stored_data['timestamp']}")
            return stored_data
            
        except (IndexError, KeyError) as e:
            logger.error(f"Error extracting data from query result: {str(e)}")
            return None
        
    except Exception as e:
        logger.error(f"Unexpected error during claim history check for '{claim_text[:50]}...': {str(e)}")
        return None

async def update_claim_history(claim_text: str, verdict: str, explanation: str, claims_collection) -> bool:
    """
    Update claim history database with new analysis results
    
    Args:
        claim_text (str): The original news claim text
        verdict (str): The verdict from LLM analysis
        explanation (str): The explanation from LLM analysis
        claims_collection: ChromaDB collection instance
    
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
        
        # Create metadata dictionary with verdict, explanation, and current UTC timestamp
        current_timestamp = datetime.utcnow().isoformat()
        metadata = {
            "verdict": verdict,
            "explanation": explanation,
            "timestamp": current_timestamp
        }
        
        logger.debug(f"Prepared metadata for claim {claim_id}: verdict={verdict}, timestamp={current_timestamp}")
        
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