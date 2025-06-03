"""
LLM utilities for the Fake News Detector
Contains functions for generating verdicts using Google Gemini
"""

import logging
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pydantic import BaseModel

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


class RefinedClaimResponse(BaseModel):
    refined_claim: str


class VerdictResponse(BaseModel):
    verdict: str
    explanation: str


class TimeDependencyResponse(BaseModel):
    is_time_dependent: bool
    dependency_duration_days: int


async def refine_claim_text(claim_text: str) -> str:
    """
    Refine the claim text using LLM to make it more suitable for web search
    
    Args:
        claim_text (str): The original news claim to refine
    
    Returns:
        str: Refined claim text optimized for web search
    """
    try:
        logger.info(f"Starting claim text refinement for: {claim_text[:100]}...")
        
        # Check if API key is configured
        if not api_key:
            logger.error("Google API key not configured")
            return claim_text
        
        # Construct prompt for claim refinement
        prompt = f"""You are an expert fact-checker. Your task is to refine the following news claim to make it more suitable for web search while preserving its core meaning.

ORIGINAL CLAIM:
{claim_text}

INSTRUCTIONS:

1. Break down the claim into specific, verifiable elements:
   - Exact numbers and quantities
   - Specific time periods
   - Precise locations
   - Specific entities or names

2. Rewrite the claim to be more searchable by:
   - Adding specific dates if time period is mentioned
   - Including full names of locations
   - Specifying exact numbers
   - Adding relevant context

3. Format the claim as a question that can be fact-checked:
   - Start with "Is it true that..."
   - Include specific details that can be verified
   - Make the claim more precise and unambiguous

4. Important rules:
   - Do not add information that wasn't in the original claim
   - Keep the refined claim concise but specific
   - If the claim is already well-formed, still format it as a question
   - Ensure the refined claim maintains the original claim's meaning

Return your response as JSON with the refined claim."""

        # Initialize Gemini model and send prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Sending prompt to Gemini API for claim refinement...")
        response = model.generate_content(
            prompt, 
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response or not response.text:
            logger.error("Empty or invalid response from Gemini API")
            return claim_text
        
        # Parse JSON response using Pydantic model
        response_data = json.loads(response.text)
        refined_response = RefinedClaimResponse(**response_data)
        
        logger.info(f"Successfully refined claim text. Original: {claim_text[:100]}... Refined: {refined_response.refined_claim[:100]}...")
        return refined_response.refined_claim
        
    except Exception as e:
        logger.error(f"Error during claim text refinement: {str(e)}")
        return claim_text

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
            search_summary = "Based on the following web search results from multiple sources:\n\n"
            for i, result in enumerate(search_results, 1):
                source = result.get('source', 'Unknown')
                search_summary += f"{i}. Title: {result.get('title', 'No title')}\n"
                search_summary += f"   Content: {result.get('snippet', 'No content')}\n"
                search_summary += f"   Source: {source}\n\n"
        else:
            search_summary = "No web search results were available for analysis.\n\n"
        
        prompt = f"""You are an expert fact-checker analyzing news claims for truthfulness. Please analyze the following claim based ONLY on the provided search results.

CLAIM TO ANALYZE:
"{claim_text}"

GROUND TRUTH (SEARCH RESULTS):
{search_summary}

INSTRUCTIONS:
1. Assess the likely truthfulness of the claim based ONLY on the provided information
2. Provide one of these verdicts: "Likely True", "Likely False", "Uncertain/Needs More Info"
3. Provide a brief explanation for your verdict
4. If search results are insufficient, indicate this in your verdict
5. Give higher priority to government sources, then news sources, then other sources

Return your response as JSON with "verdict" and "explanation" fields."""

        # Initialize Gemini model and send prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Sending prompt to Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response or not response.text:
            logger.error("Empty or invalid response from Gemini API")
            return {
                "verdict": "Error",
                "explanation": "No response received from LLM service"
            }
        
        logger.info("Received response from Gemini API, parsing JSON results...")
        
        # Parse JSON response using Pydantic model
        response_data = json.loads(response.text)
        verdict_response = VerdictResponse(**response_data)
        
        logger.info(f"LLM analysis completed successfully - Verdict: {verdict_response.verdict}")
        
        return {
            "verdict": verdict_response.verdict,
            "explanation": verdict_response.explanation
        }
        
    except Exception as e:
        logger.error(f"Error during LLM analysis: {str(e)}")
        return {
            "verdict": "Error",
            "explanation": f"Analysis failed due to technical error: {str(e)}"
        }

async def check_time_dependency(claim_text: str) -> dict:
    """
    Check if a claim is time-dependent and determine its dependency duration
    
    Args:
        claim_text (str): The news claim to analyze for time dependency
    
    Returns:
        dict: Dictionary containing 'is_time_dependent' and 'dependency_duration_days'
    """
    try:
        logger.info(f"Checking time dependency for claim: {claim_text[:100]}...")
        
        # Check if API key is configured
        if not api_key:
            logger.error("Google API key not configured")
            return {
                "is_time_dependent": False,
                "dependency_duration_days": 0
            }
        
        # Construct prompt for time dependency analysis
        prompt = f"""You are an expert fact-checker analyzing news claims for time dependency. Analyze the following claim to determine if its truthfulness depends on current or recent events that change over time.

CLAIM TO ANALYZE:
"{claim_text}"

INSTRUCTIONS:

1. Determine if this claim is time-dependent by checking if it relates to:
   - Current events (politics, breaking news, ongoing situations)
   - Stock prices, market conditions, or financial data
   - Weather or environmental conditions
   - Sports scores, rankings, or current competitions
   - Real-time statistics or data
   - Ongoing conflicts, elections, or political situations
   - Current policies, laws, or regulations that change frequently
   - Social media trends or viral content
   - Technology updates, software versions, or product releases

2. If the claim is time-dependent, estimate how many days the information remains relevant:
   - Breaking news, stock prices, weather: 1-3 days
   - Political developments, ongoing events: 7-14 days
   - Sports seasons, quarterly reports: 30-90 days
   - Annual statistics, yearly reports: 180-365 days

3. If the claim is NOT time-dependent, it includes:
   - Historical facts and events
   - Scientific principles and laws
   - Biographical information
   - Geographic facts
   - Mathematical or logical statements
   - Established scientific discoveries

Return your response as JSON with "is_time_dependent" (boolean) and "dependency_duration_days" (integer) fields only."""

        # Initialize Gemini model and send prompt
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        logger.info("Sending time dependency analysis prompt to Gemini API...")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        if not response or not response.text:
            logger.error("Empty or invalid response from Gemini API for time dependency check")
            return {
                "is_time_dependent": False,
                "dependency_duration_days": 0
            }
        
        logger.info("Received time dependency response from Gemini API, parsing JSON results...")
        
        # Parse JSON response using Pydantic model
        response_data = json.loads(response.text)
        time_dependency_response = TimeDependencyResponse(**response_data)
        
        logger.info(f"Time dependency analysis completed - Is time dependent: {time_dependency_response.is_time_dependent}, Duration: {time_dependency_response.dependency_duration_days} days")
        
        return {
            "is_time_dependent": time_dependency_response.is_time_dependent,
            "dependency_duration_days": time_dependency_response.dependency_duration_days
        }
        
    except Exception as e:
        logger.error(f"Error during time dependency analysis: {str(e)}")
        return {
            "is_time_dependent": False,
            "dependency_duration_days": 0
        } 