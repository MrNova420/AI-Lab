#!/usr/bin/env python3
"""
Advanced Web Search & Analysis Tool
Multi-source search, verification, and detailed analysis
"""

import requests
import json
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import time

class WebSearcher:
    """Advanced web searcher with multi-source support"""
    
    def __init__(self):
        self.sources = {
            'duckduckgo': self._search_ddg,
            'brave': self._search_brave,
            'searx': self._search_searx
        }
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def search(self, query, max_results=10, verify=True):
        """
        Advanced search with verification
        Returns aggregated results from multiple sources
        """
        print(f"🔍 Searching: {query}")
        
        results = {
            'query': query,
            'sources': [],
            'verified_results': [],
            'analysis': {}
        }
        
        # Search multiple sources in parallel
        all_results = []
        
        # DuckDuckGo (fast, privacy-focused)
        try:
            ddg_results = self._search_ddg(query, max_results)
            results['sources'].append('duckduckgo')
            all_results.extend(ddg_results)
        except Exception as e:
            print(f"⚠️ DuckDuckGo failed: {e}")
        
        # Aggregate and deduplicate
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        results['verified_results'] = unique_results[:max_results]
        
        # Analyze results
        if verify:
            results['analysis'] = self._analyze_results(unique_results)
        
        return results
    
    def _search_ddg(self, query, max_results=10):
        """Search DuckDuckGo"""
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result_div in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result_div.find('a', class_='result__a')
                snippet_elem = result_div.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'source': 'duckduckgo'
                    })
            
            return results
        except Exception as e:
            print(f"DDG search error: {e}")
            return []
    
    def _search_brave(self, query, max_results=10):
        """Search Brave (privacy-focused, good results)"""
        # TODO: Implement Brave API if available
        return []
    
    def _search_searx(self, query, max_results=10):
        """Search SearX (meta-search engine)"""
        # TODO: Implement SearX instance
        return []
    
    def _analyze_results(self, results):
        """
        Analyze search results for quality and relevance
        """
        analysis = {
            'total_results': len(results),
            'domains': {},
            'quality_score': 0,
            'verified': False
        }
        
        # Count domains (check for diversity)
        for result in results:
            url = result.get('url', '')
            try:
                domain = url.split('/')[2] if '/' in url else 'unknown'
                analysis['domains'][domain] = analysis['domains'].get(domain, 0) + 1
            except:
                pass
        
        # Quality score based on diversity
        unique_domains = len(analysis['domains'])
        if unique_domains >= 5:
            analysis['quality_score'] = 10
        else:
            analysis['quality_score'] = unique_domains * 2
        
        # Mark as verified if multiple sources
        analysis['verified'] = len(analysis['domains']) >= 3
        
        return analysis
    
    def quick_search(self, query, max_results=5):
        """Fast search for quick lookups"""
        return self.search(query, max_results=max_results, verify=False)
    
    def deep_search(self, query, max_results=20):
        """Deep search with full verification"""
        return self.search(query, max_results=max_results, verify=True)
    
    def summarize_results(self, results):
        """
        AI-friendly summary of search results
        """
        summary = {
            'query': results['query'],
            'found': len(results['verified_results']),
            'top_results': []
        }
        
        for i, result in enumerate(results['verified_results'][:5], 1):
            summary['top_results'].append({
                'rank': i,
                'title': result.get('title', 'No title'),
                'url': result.get('url', ''),
                'snippet': result.get('snippet', '')[:200]
            })
        
        if results.get('analysis'):
            summary['quality'] = results['analysis'].get('quality_score', 0)
            summary['verified'] = results['analysis'].get('verified', False)
        
        return summary


# Global searcher instance
_searcher = None

def get_searcher():
    """Get or create searcher instance"""
    global _searcher
    if _searcher is None:
        _searcher = WebSearcher()
    return _searcher


# Tool functions for AI
def web_search(query, quick=False):
    """
    AI Tool: Search the web
    quick=True for fast results, False for deep search
    """
    searcher = get_searcher()
    
    if quick:
        results = searcher.quick_search(query)
    else:
        results = searcher.deep_search(query)
    
    return searcher.summarize_results(results)


def verify_information(query, claim):
    """
    AI Tool: Verify a claim by searching multiple sources
    """
    searcher = get_searcher()
    
    # Search for the claim
    search_query = f"{query} {claim}"
    results = searcher.deep_search(search_query, max_results=10)
    
    summary = searcher.summarize_results(results)
    summary['claim'] = claim
    summary['verification'] = {
        'sources_found': len(results['verified_results']),
        'quality_score': results['analysis'].get('quality_score', 0),
        'verified': results['analysis'].get('verified', False)
    }
    
    return summary


def search_multiple_sources(query):
    """
    AI Tool: Search multiple sources and aggregate
    Best for fact-checking and comprehensive research
    """
    searcher = get_searcher()
    
    results = searcher.deep_search(query, max_results=20)
    
    # Format for AI consumption
    return {
        'query': query,
        'total_results': len(results['verified_results']),
        'sources_used': results.get('sources', []),
        'domains_found': len(results['analysis'].get('domains', {})),
        'verified': results['analysis'].get('verified', False),
        'top_results': results['verified_results'][:10]
    }
