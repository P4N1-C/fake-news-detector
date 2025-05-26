"""
AI-Powered Fake News Detector - Backend API
Main FastAPI application with health check endpoint
"""

import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from duckduckgo_search import DDGS
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Google Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Google Gemini API configured successfully")
else:
    logger.error("GOOGLE_API_KEY not found in environment variables")

# Web search utility function
async def search_web(query: str, max_results: int = 3) -> list:
    """
    Asynchronous function to search the web using DuckDuckGo
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 3)
    
    Returns:
        list: List of dictionaries containing 'title' and 'snippet' for each result
    """
    try:
        logger.info(f"Starting web search for query: {query[:100]}...")
        
        # Initialize DuckDuckGo search
        ddgs = DDGS()
        
        # Perform text search and get results
        search_results = []
        results = ddgs.text(query, max_results=max_results)
        
        for result in results:
            search_result = {
                "title": result.get("title", "No title available"),
                "snippet": result.get("body", "No snippet available")
            }
            search_results.append(search_result)
        
        logger.info(f"Web search completed successfully. Found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error during web search for query '{query}': {str(e)}")
        # Return empty list on error to allow graceful degradation
        return []

# LLM verdict generation function
async def get_llm_verdict(claim_text: str, search_results: list) -> dict:
    """
    Generate verdict and explanation using Google Gemini LLM
    
    Args:
        claim_text (str): The original news claim to analyze
        search_results (list): List of search result dictionaries with 'title' and 'snippet'
    
    Returns:
        dict: Dictionary containing 'verdict' and 'explanation' keys
    """
    try:
        logger.info(f"Starting LLM analysis for claim: {claim_text[:100]}...")
        
        # Check if API key is configured
        if not api_key:
            logger.error("Google API key not configured")
            return {
                "verdict": "Error",
                "explanation": "LLM service not available - API key not configured"
            }
        
        # Construct detailed prompt for Gemini model
        search_summary = ""
        if search_results:
            search_summary = "Based on the following web search results:\n\n"
            for i, result in enumerate(search_results, 1):
                search_summary += f"{i}. Title: {result.get('title', 'No title')}\n"
                search_summary += f"   Content: {result.get('snippet', 'No content')}\n\n"
        else:
            search_summary = "No web search results were available for analysis.\n\n"
        
        prompt = f"""You are an expert fact-checker analyzing news claims for truthfulness. Please analyze the following claim based ONLY on the provided search results.

CLAIM TO ANALYZE:
"{claim_text}"

{search_summary}

INSTRUCTIONS:
1. Assess the likely truthfulness of the claim based ONLY on the provided information
2. Provide one of these verdicts: "Likely True", "Likely False", "Uncertain/Needs More Info"
3. Provide a brief explanation for your verdict
4. If search results are insufficient, indicate this in your verdict

REQUIRED RESPONSE FORMAT:
Verdict: [Your verdict here]
Explanation: [Your detailed explanation here]

Please respond with only the verdict and explanation in the exact format specified above."""

        # Initialize Gemini model and send prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Sending prompt to Gemini API...")
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            logger.error("Empty or invalid response from Gemini API")
            return {
                "verdict": "Error",
                "explanation": "No response received from LLM service"
            }
        
        logger.info("Received response from Gemini API, parsing results...")
        
        # Parse the LLM response to extract verdict and explanation
        response_text = response.text.strip()
        
        # Initialize default values
        verdict = "Uncertain/Needs More Info"
        explanation = "Unable to parse LLM response properly"
        
        # Split response into lines for parsing
        lines = response_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith("Verdict:"):
                verdict = line.replace("Verdict:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
        
        # If explanation is still default, try to extract from full response
        if explanation == "Unable to parse LLM response properly":
            # Look for explanation after verdict
            verdict_found = False
            explanation_parts = []
            for line in lines:
                line = line.strip()
                if line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
                    verdict_found = True
                elif verdict_found and line:
                    explanation_parts.append(line)
            
            if explanation_parts:
                explanation = " ".join(explanation_parts)
        
        # Validate that we have meaningful content
        if not verdict or verdict == "":
            verdict = "Uncertain/Needs More Info"
        if not explanation or explanation == "":
            explanation = "No detailed explanation provided by the analysis system"
        
        logger.info(f"LLM analysis completed successfully - Verdict: {verdict}")
        
        return {
            "verdict": verdict,
            "explanation": explanation
        }
        
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}")
        return {
            "verdict": "Error",
            "explanation": f"Analysis failed due to technical error: {str(e)}"
        }

# Pydantic models
class ClaimRequest(BaseModel):
    claim_text: str

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
    API endpoint for claim submission and analysis
    Step 2.3: Integrates LLM processing into claim analysis endpoint
    """
    try:
        logger.info(f"Received claim analysis request: {request.claim_text[:100]}...")
        
        # Step 1.4: Call web search function using claim_text as query
        logger.info("Starting web search for claim analysis...")
        search_results = await search_web(request.claim_text)
        
        # Step 2.3: Call LLM verdict generation function
        logger.info("Starting LLM analysis for claim verification...")
        llm_result = await get_llm_verdict(request.claim_text, search_results)
        
        # Build response with claim, search results, verdict and explanation
        response = {
            "received_claim": request.claim_text,
            "search_results": search_results,
            "verdict": llm_result["verdict"],
            "explanation": llm_result["explanation"]
        }
        
        logger.info(f"Successfully completed claim analysis pipeline - Verdict: {llm_result['verdict']}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing claim analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error processing claim analysis")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True) 