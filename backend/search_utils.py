"""
Web search utilities for the Fake News Detector
Contains functions for searching using SerpAPI, DuckDuckGo, and Tavily
"""

import logging
import os
import asyncio
from duckduckgo_search import DDGS
from serpapi import GoogleSearch
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure SerpAPI
serpapi_key = os.getenv("SERPAPI_KEY")
if serpapi_key:
    logger.info("SerpAPI key configured successfully")
else:
    logger.warning("SERPAPI_KEY not found in environment variables - SerpAPI search will be disabled")

# Configure Tavily API
tavily_key = os.getenv("TAVILY_API_KEY")
if tavily_key:
    logger.info("Tavily API key found in environment variables")
    if tavily_key == "your_tavily_api_key_here":
        logger.error("Tavily API key is still set to the default value. Please update it in .env file")
        tavily_client = None
    else:
        tavily_client = TavilyClient(api_key=tavily_key)
        logger.info("Tavily API configured successfully")
else:
    tavily_client = None
    logger.error("TAVILY_API_KEY not found in environment variables - Tavily search will be disabled")

async def search_serpapi(query: str, max_results: int = 3) -> list:
    """
    Asynchronous function to search the web using SerpAPI
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 3)
    
    Returns:
        list: List of dictionaries containing 'title' and 'snippet' for each result
    """
    try:
        if not serpapi_key:
            logger.warning("SerpAPI key not configured, skipping SerpAPI search")
            return []
        
        logger.info(f"Starting SerpAPI search for query: {query[:100]}...")
        
        # Configure SerpAPI search parameters
        search_params = {
            "engine": "google",
            "q": query,
            "api_key": serpapi_key,
            "num": max_results,
            "safe": "active"
        }
        
        # Perform search
        search = GoogleSearch(search_params)
        results = search.get_dict()
        
        search_results = []
        
        # Extract organic results
        if "organic_results" in results:
            for result in results["organic_results"][:max_results]:
                search_result = {
                    "title": result.get("title", "No title available"),
                    "snippet": result.get("snippet", "No snippet available"),
                    "url": result.get("link", "No URL available"),
                    "source": "SerpAPI"
                }
                search_results.append(search_result)
        
        logger.info(f"SerpAPI search completed successfully. Found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error during SerpAPI search for query '{query}': {str(e)}")
        return []

async def search_duckduckgo(query: str, max_results: int = 3) -> list:
    """
    Asynchronous function to search the web using DuckDuckGo
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 3)
    
    Returns:
        list: List of dictionaries containing 'title' and 'snippet' for each result
    """
    try:
        logger.info(f"Starting DuckDuckGo search for query: {query[:100]}...")
        
        # Initialize DuckDuckGo search
        ddgs = DDGS()
        
        # Perform text search and get results
        search_results = []
        results = ddgs.text(query, max_results=max_results)
        
        for result in results:
            search_result = {
                "title": result.get("title", "No title available"),
                "snippet": result.get("body", "No snippet available"),
                "url": result.get("href", "No URL available"),
                "source": "DuckDuckGo"
            }
            search_results.append(search_result)
        
        logger.info(f"DuckDuckGo search completed successfully. Found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error during DuckDuckGo search for query '{query}': {str(e)}")
        return []

async def search_tavily(query: str, max_results: int = 3) -> list:
    """
    Asynchronous function to search the web using Tavily AI
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 3)
    
    Returns:
        list: List of dictionaries containing 'title' and 'snippet' for each result
    """
    try:
        if not tavily_client:
            logger.warning("Tavily API key not configured, skipping Tavily search")
            return []
        
        logger.info(f"Starting Tavily search for query: {query[:100]}...")
        
        # Perform search using Tavily
        search_response = tavily_client.search(
            query=query,
            search_depth="basic",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False
        )
        
        logger.info(f"Raw Tavily response type: {type(search_response)}")
        logger.info(f"Raw Tavily response: {search_response}")
        
        search_results = []
        
        # Extract results from Tavily response
        if isinstance(search_response, dict) and "results" in search_response:
            results = search_response["results"]
        elif isinstance(search_response, list):
            results = search_response
        else:
            logger.warning(f"Unexpected Tavily response structure: {search_response}")
            return []
        
        # Process each result
        for result in results[:max_results]:
            logger.info(f"Processing Tavily result: {result}")
            
            title = result.get("title") or result.get("Title") or "No title available"
            content = result.get("content") or result.get("Content") or result.get("snippet") or result.get("Snippet") or "No content available"
            url = result.get("url") or result.get("URL") or result.get("link") or "No URL available"
            
            search_result = {
                "title": title,
                "snippet": content,
                "url": url,
                "source": "Tavily"
            }
            search_results.append(search_result)
            logger.info(f"Added Tavily result: {search_result}")
        
        logger.info(f"Tavily search completed successfully. Found {len(search_results)} results")
        return search_results
        
    except Exception as e:
        logger.error(f"Error during Tavily search for query '{query}': {str(e)}")
        logger.exception("Full traceback:")
        return []

async def search_web(query: str, max_results: int = 9) -> list:
    """
    Asynchronous function to search the web using SerpAPI, DuckDuckGo, and Tavily
    
    Args:
        query (str): Search query string
        max_results (int): Maximum number of results to return (default: 9)
    
    Returns:
        list: List of dictionaries containing 'title', 'snippet', 'url', and 'source' for each result
    """
    try:
        logger.info(f"Starting combined web search for query: {query[:100]}...")
        
        # Calculate results per search engine (divide by 3, minimum 2 each)
        results_per_engine = max(2, max_results // 3)
        
        # Run all three searches concurrently
        serpapi_task = search_serpapi(query, results_per_engine)
        duckduckgo_task = search_duckduckgo(query, results_per_engine)
        tavily_task = search_tavily(query, results_per_engine)
        
        # Wait for all searches to complete
        serpapi_results, duckduckgo_results, tavily_results = await asyncio.gather(
            serpapi_task, duckduckgo_task, tavily_task, return_exceptions=True
        )
        
        # Handle exceptions from async tasks
        if isinstance(tavily_results, Exception):
            logger.error(f"Tavily search failed: {tavily_results}")
            tavily_results = []
        if isinstance(serpapi_results, Exception):
            logger.error(f"SerpAPI search failed: {serpapi_results}")
            serpapi_results = []
        if isinstance(duckduckgo_results, Exception):
            logger.error(f"DuckDuckGo search failed: {duckduckgo_results}")
            duckduckgo_results = []
        
        # Log results from each engine
        logger.info(f"SerpAPI found {len(serpapi_results)} results")
        logger.info(f"DuckDuckGo found {len(duckduckgo_results)} results")
        logger.info(f"Tavily found {len(tavily_results)} results")
        
        # Combine results from all search engines
        combined_results = []
        seen_titles = set()  # Keep track of unique titles
        
        # Helper function to add unique results
        def add_unique_results(results):
            for result in results:
                title = result.get("title", "").lower().strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    combined_results.append(result)
        
        # Add results in order of preference (Tavily first, then SerpAPI, then DuckDuckGo)
        if tavily_results:
            add_unique_results(tavily_results)
            logger.info(f"Added {len(tavily_results)} Tavily results")
        
        if serpapi_results:
            add_unique_results(serpapi_results)
            logger.info(f"Added {len(serpapi_results)} SerpAPI results")
        
        if duckduckgo_results:
            add_unique_results(duckduckgo_results)
            logger.info(f"Added {len(duckduckgo_results)} DuckDuckGo results")
        
        # Limit to max_results
        final_results = combined_results[:max_results]
        logger.info(f"Combined web search completed. Returning {len(final_results)} unique results")
        return final_results
        
    except Exception as e:
        logger.error(f"Error during combined web search for query '{query}': {str(e)}")
        logger.exception("Full traceback:")
        # Fallback to DuckDuckGo only on error
        try:
            return await search_duckduckgo(query, max_results)
        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {fallback_error}")
            return [] 