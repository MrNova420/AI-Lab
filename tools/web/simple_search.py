#!/usr/bin/env python3
"""
Simple Web Search - Works with any AI model
Uses DuckDuckGo HTML search (no API key needed)
"""

import requests
from urllib.parse import quote_plus

# Try to import BeautifulSoup, but work without it
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except:
    HAS_BS4 = False


def search_web(query, max_results=5):
    """
    Search the web using DuckDuckGo
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 5)
        
    Returns:
        Dict with search results
    """
    if not HAS_BS4:
        # Fallback: Just return search URL
        return {
            'success': True,
            'query': query,
            'message': f"Search: {query}",
            'url': f"https://duckduckgo.com/?q={quote_plus(query)}",
            'note': 'Install beautifulsoup4 for actual results: pip install beautifulsoup4'
        }
    
    try:
        # Use DuckDuckGo HTML search (no API needed)
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f"Search failed with status {response.status_code}",
                'query': query
            }
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result_div in soup.find_all('div', class_='result')[:max_results]:
            try:
                title_elem = result_div.find('a', class_='result__a')
                snippet_elem = result_div.find('a', class_='result__snippet')
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ''
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })
            except Exception:
                continue
        
        return {
            'success': True,
            'query': query,
            'results': results,
            'count': len(results),
            'message': f"Found {len(results)} results for '{query}'"
        }
        
    except requests.Timeout:
        return {
            'success': False,
            'error': 'Search timed out',
            'query': query
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Search error: {str(e)}",
            'query': query
        }


# Alternative simple search if beautifulsoup not available
def simple_search_web(query):
    """
    Very simple web search fallback
    Just returns a helpful message
    """
    return {
        'success': True,
        'query': query,
        'message': f"To search for '{query}', visit: https://duckduckgo.com/?q={quote_plus(query)}",
        'url': f"https://duckduckgo.com/?q={quote_plus(query)}"
    }
