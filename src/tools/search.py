import logging
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("SEARCH")

@tool
def search_web(query: str) -> str:
    """Search the webs for URLs with a query"""
    log.info('Searching: "%s"', query)
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    response = tavily_client.search(query)
    results = response.get("results", [])
    log.info("Found %d results", len(results))
    return response
