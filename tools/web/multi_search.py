"""
Multi-Source Web Search - Combines multiple search engines
"""

import asyncio
import aiohttp
from typing import Dict, List
import json
from bs4 import BeautifulSoup

class MultiSourceSearch:
    """Orchestrates searches across multiple engines"""
    
    def __init__(self):
        self.sources = {
            'grokipedia': True,   # PRIMARY
            'google': True,
            'bing': True,
            'duckduckgo': True,
            'wikipedia': True
        }
        print("🌐 Multi-Source Search initialized")
        print(f"   Active sources: {', '.join([s for s, enabled in self.sources.items() if enabled])}")
    
    async def search_all(self, query: str) -> Dict:
        """
        Search ALL sources in parallel for maximum coverage
        
        Returns comprehensive results from all sources
        """
        print(f"\n🔍 Multi-Source Search: '{query}'")
        print("=" * 60)
        
        results = {
            'query': query,
            'sources': {},
            'combined_content': '',
            'all_sources': [],
            'confidence': 0.0
        }
        
        # Create tasks for parallel search
        tasks = []
        
        if self.sources.get('grokipedia'):
            tasks.append(self._search_grokipedia(query))
        if self.sources.get('google'):
            tasks.append(self._search_google(query))
        if self.sources.get('duckduckgo'):
            tasks.append(self._search_duckduckgo(query))
        if self.sources.get('wikipedia'):
            tasks.append(self._search_wikipedia(query))
        
        # Execute all searches in parallel
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for source_result in search_results:
            if isinstance(source_result, dict) and source_result.get('found'):
                source_name = source_result['source']
                results['sources'][source_name] = source_result
                
                # Combine content
                if source_result.get('content'):
                    results['combined_content'] += f"\n\n### From {source_name}:\n{source_result['content'][:500]}"
                
                # Collect all source links
                results['all_sources'].extend(source_result.get('sources', []))
        
        # Calculate overall confidence
        if results['sources']:
            confidences = [s['confidence'] for s in results['sources'].values() if 'confidence' in s]
            results['confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
        
        print(f"\n✅ Found results from {len(results['sources'])} sources")
        print(f"   Overall confidence: {results['confidence']:.2%}")
        
        return results
    
    async def _search_grokipedia(self, query: str) -> Dict:
        """Search Grokipedia (PRIMARY SOURCE)"""
        print("  → Searching Grokipedia...")
        try:
            from tools.web.grokipedia import GrokipediaSearch
            grok = GrokipediaSearch()
            result = grok.search(query, deep_search=True)
            print(f"    ✓ Grokipedia: {'Found' if result['found'] else 'No results'}")
            return result
        except Exception as e:
            print(f"    ✗ Grokipedia error: {e}")
            return {'found': False, 'source': 'Grokipedia', 'error': str(e)}
    
    async def _search_google(self, query: str) -> Dict:
        """Search Google via scraping"""
        print("  → Searching Google...")
        try:
            url = f"https://www.google.com/search?q={query}"
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                async with session.get(url, headers=headers, timeout=10) as response:
                    html = await response.text()
                    
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract search results
                    results = []
                    for g in soup.find_all('div', class_='g')[:5]:
                        title_elem = g.find('h3')
                        link_elem = g.find('a')
                        snippet_elem = g.find('div', class_='VwiC3b')
                        
                        if title_elem and link_elem:
                            results.append({
                                'title': title_elem.get_text(),
                                'url': link_elem.get('href', ''),
                                'snippet': snippet_elem.get_text() if snippet_elem else ''
                            })
                    
                    content = '\n'.join([f"{r['title']}\n{r['snippet']}" for r in results])
                    
                    print(f"    ✓ Google: Found {len(results)} results")
                    return {
                        'found': len(results) > 0,
                        'query': query,
                        'content': content,
                        'sources': results,
                        'confidence': 0.85,
                        'source': 'Google'
                    }
        except Exception as e:
            print(f"    ✗ Google error: {e}")
            return {'found': False, 'source': 'Google', 'error': str(e)}
    
    async def _search_duckduckgo(self, query: str) -> Dict:
        """Search DuckDuckGo"""
        print("  → Searching DuckDuckGo...")
        try:
            url = f"https://duckduckgo.com/html/?q={query}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for result in soup.find_all('div', class_='result')[:5]:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem:
                            results.append({
                                'title': title_elem.get_text(),
                                'url': title_elem.get('href', ''),
                                'snippet': snippet_elem.get_text() if snippet_elem else ''
                            })
                    
                    content = '\n'.join([f"{r['title']}\n{r['snippet']}" for r in results])
                    
                    print(f"    ✓ DuckDuckGo: Found {len(results)} results")
                    return {
                        'found': len(results) > 0,
                        'query': query,
                        'content': content,
                        'sources': results,
                        'confidence': 0.80,
                        'source': 'DuckDuckGo'
                    }
        except Exception as e:
            print(f"    ✗ DuckDuckGo error: {e}")
            return {'found': False, 'source': 'DuckDuckGo', 'error': str(e)}
    
    async def _search_wikipedia(self, query: str) -> Dict:
        """Search Wikipedia"""
        print("  → Searching Wikipedia...")
        try:
            url = f"https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': query,
                'srlimit': 3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    data = await response.json()
                    
                    results = []
                    if 'query' in data and 'search' in data['query']:
                        for item in data['query']['search']:
                            results.append({
                                'title': item['title'],
                                'url': f"https://en.wikipedia.org/wiki/{item['title'].replace(' ', '_')}",
                                'snippet': item['snippet']
                            })
                    
                    content = '\n'.join([f"{r['title']}\n{r['snippet']}" for r in results])
                    
                    print(f"    ✓ Wikipedia: Found {len(results)} results")
                    return {
                        'found': len(results) > 0,
                        'query': query,
                        'content': content,
                        'sources': results,
                        'confidence': 0.90,
                        'source': 'Wikipedia'
                    }
        except Exception as e:
            print(f"    ✗ Wikipedia error: {e}")
            return {'found': False, 'source': 'Wikipedia', 'error': str(e)}


async def search(query: str) -> Dict:
    """Main search function - use this in the AI system"""
    searcher = MultiSourceSearch()
    return await searcher.search_all(query)


if __name__ == "__main__":
    # Test
    result = asyncio.run(search("quantum computing"))
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(json.dumps({k: v for k, v in result.items() if k != 'combined_content'}, indent=2))
