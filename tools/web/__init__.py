"""
Web Search Tool Registry - Production Multi-Source Search
"""

from tools.web.multi_search import search as multi_search
import asyncio

async def production_web_search(query: str) -> dict:
    """
    Production web search using ALL sources:
    - Grokipedia (primary, verified)
    - Google (comprehensive)
    - DuckDuckGo (privacy-focused)
    - Wikipedia (encyclopedia)
    
    Returns comprehensive, verified results
    """
    return await multi_search(query)


def web_search(query: str) -> dict:
    """Synchronous wrapper for web search"""
    return asyncio.run(production_web_search(query))


# Tool definition for AI system
TOOL_DEFINITION = {
    "name": "web_search",
    "description": """Search the entire web using multiple sources (Grokipedia, Google, Wikipedia, DuckDuckGo) 
    to find accurate, verified, up-to-date information. Use this when you need current facts, 
    research, or information not in your training data.""",
    "parameters": {
        "query": "The search query or question to research"
    },
    "returns": "Comprehensive search results from multiple verified sources",
    "function": web_search
}
