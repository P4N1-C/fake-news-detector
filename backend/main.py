"""
AI-Powered Fake News Detector - Backend API
Main FastAPI application with health check endpoint
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from search_utils import search_web
from llm_utils import get_llm_verdict, refine_claim_text
from db_utils import check_claim_history, update_claim_history, generate_claim_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize ChromaDB client and collection
def initialize_chromadb():
    """
    Initialize persistent ChromaDB client and claims_history collection
    """
    try:
        # Specify local path for ChromaDB data storage
        chroma_db_path = "./chroma_db_data"
        
        logger.info(f"Initializing ChromaDB client with persistent storage at: {chroma_db_path}")
        
        # Initialize persistent ChromaDB client
        chroma_client = chromadb.PersistentClient(path=chroma_db_path)
        
        # Create embedding function using SentenceTransformer
        embedding_function = SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create claims_history collection with embedding function
        claims_collection = chroma_client.get_or_create_collection(
            name="claims_history",
            embedding_function=embedding_function
        )
        
        logger.info(f"Successfully initialized ChromaDB collection 'claims_history'")
        logger.info(f"Collection contains {claims_collection.count()} existing entries")
        
        return chroma_client, claims_collection
        
    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {str(e)}")
        raise e

# Initialize ChromaDB at startup
try:
    chroma_client, claims_collection = initialize_chromadb()
    logger.info("ChromaDB initialization completed successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {str(e)}")
    # For MVP, we'll continue without database if initialization fails
    chroma_client = None
    claims_collection = None

# Pydantic models
class ClaimRequest(BaseModel):
    claim_text: str

class FeedbackRequest(BaseModel):
    claim_text: str
    feedback_type: str  # "accurate" or "inaccurate"

# Initialize FastAPI application
app = FastAPI(
    title="AI-Powered Fake News Detector",
    description="Backend API for analyzing news claims using web search and LLM",
    version="1.0.0"
)

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.post("/analyze_claim")
async def analyze_claim(request: ClaimRequest):
    """
    API endpoint for claim submission and analysis with claim history integration
    """
    try:
        logger.info(f"Received claim analysis request: {request.claim_text[:100]}...")
        
        # Step 1: Check claim history first
        logger.info("Checking claim history for existing analysis...")
        historical_entry = await check_claim_history(request.claim_text, claims_collection)
        
        if historical_entry:
            # Return historical data if found
            logger.info(f"Found existing analysis in claim history - Verdict: {historical_entry['verdict']}")
            response = {
                "received_claim": request.claim_text,
                "verdict": historical_entry["verdict"],
                "explanation": historical_entry["explanation"],
                "source": "claim_history",
                "timestamp": historical_entry["timestamp"],
                "source_links": historical_entry.get("source_links", [])
            }
            return response
        
        # Step 2: No historical entry found, proceed with new analysis
        logger.info("No historical entry found, proceeding with new analysis...")
        
        # Step 3: Refine the claim text using LLM
        logger.info("Starting claim text refinement...")
        refined_claim = await refine_claim_text(request.claim_text)
        
        # Step 4: Call web search function using refined claim as query
        logger.info("Starting web search for claim analysis...")
        search_results = await search_web(refined_claim)
        
        # Step 5: Call LLM verdict generation function
        logger.info("Starting LLM analysis for claim verification...")
        llm_result = await get_llm_verdict(request.claim_text, search_results)
        
        # Step 6: Update claim history database with new analysis
        logger.info("Saving new analysis to claim history database...")
        update_success = await update_claim_history(
            request.claim_text, 
            llm_result["verdict"], 
            llm_result["explanation"], 
            claims_collection,
            search_results
        )
        
        if update_success:
            logger.info("Successfully saved new analysis to claim history database")
        else:
            logger.warning("Failed to save new analysis to claim history database")
        
        # Build response with original claim, refined claim, search results, verdict and explanation
        response = {
            "received_claim": request.claim_text,
            "refined_claim": refined_claim,
            "search_results": search_results,
            "verdict": llm_result["verdict"],
            "explanation": llm_result["explanation"],
            "source": "new_analysis"
        }
        
        logger.info(f"Successfully completed claim analysis pipeline - Verdict: {llm_result['verdict']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing claim analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing claim analysis")

@app.post("/submit_feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    API endpoint for receiving user feedback on claim analysis accuracy
    """
    try:
        logger.info(f"Received feedback - Claim: {request.claim_text[:50]}... | Feedback: {request.feedback_type}")
        
        # Generate the claim ID using same method as database operations
        claim_id = generate_claim_id(request.claim_text)
        
        # Try to retrieve the existing entry from ChromaDB
        if claims_collection:
            try:
                query_result = claims_collection.get(
                    ids=[claim_id],
                    include=["metadatas", "documents"]
                )
                
                if query_result['ids']:
                    # Entry found, update metadata with feedback
                    current_metadata = query_result['metadatas'][0] if query_result['metadatas'] else {}
                    
                    # Add feedback to metadata
                    from datetime import datetime
                    current_metadata['user_feedback'] = request.feedback_type
                    current_metadata['feedback_timestamp'] = datetime.utcnow().isoformat()
                    
                    # Update the entry
                    claims_collection.update(
                        ids=[claim_id],
                        metadatas=[current_metadata]
                    )
                    
                    logger.info(f"Successfully updated claim {claim_id} with feedback: {request.feedback_type}")
                    return {"message": "Feedback submitted and logged successfully.", "status": "success"}
                else:
                    logger.warning(f"Claim not found in database for feedback: {claim_id}")
                    return {"message": "Feedback logged but claim not found in database.", "status": "logged"}
                    
            except Exception as db_error:
                logger.error(f"Database error while updating feedback: {str(db_error)}")
                return {"message": "Feedback logged but database update failed.", "status": "error"}
        else:
            logger.warning("ChromaDB not available, feedback only logged to console")
            return {"message": "Feedback logged successfully.", "status": "logged"}
            
    except Exception as e:
        logger.error(f"Error processing feedback submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing feedback")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 