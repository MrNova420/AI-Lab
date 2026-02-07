#!/usr/bin/env python3
"""
🌟 Grokipedia-Focused Search System
Testing if Grokipedia alone can provide faster, more accurate results than multi-source

HYPOTHESIS:
- Grokipedia updates every minute (more current than Wikipedia)
- Grokipedia has in-depth, analyzed, verified content
- Using ONLY Grokipedia might be faster AND better than multiple sources
- Could simplify web search dramatically

TEST GOALS:
1. Speed: Can we get <3 second responses?
2. Accuracy: Is content verified and accurate?
3. Coverage: Does it cover enough topics?
4. Depth: Is content detailed enough for research?
"""

import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from datetime import datetime
import time
from typing import Dict, List, Optional


class GrokipediaEngine:
    """
    Optimized Grokipedia search engine
    Focus: Speed + Accuracy + Depth
    """
    
    def __init__(self):
        self.base_url = "https://grokipedia.com"
        self.timeout = 5  # Very fast timeout
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        self.cache = {}  # Cache for speed
        
    def get_headers(self):
        """Get request headers"""
        return {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
    
    def search_article(self, query: str) -> Optional[Dict]:
        """
        Search for a specific article directly
        FAST: Direct article access
        """
        start_time = time.time()
        print(f"🌟 Searching Grokipedia: {query}")
        
        try:
            # Try direct article URL (fastest)
            article_slug = query.replace(' ', '_')
            url = f"{self.base_url}/wiki/{quote_plus(article_slug)}"
            
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract comprehensive content
                result = self._extract_article_content(soup, url)
                
                elapsed = time.time() - start_time
                result['search_time'] = f"{elapsed:.2f}s"
                
                print(f"✅ Found article in {elapsed:.2f}s")
                return result
            else:
                print(f"⚠️ Direct article not found (HTTP {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return None
    
    def search_general(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        General search when direct article not found
        Returns list of relevant articles
        """
        start_time = time.time()
        print(f"🔍 General search on Grokipedia: {query}")
        
        results = []
        
        try:
            # Try search page
            search_url = f"{self.base_url}/search?q={quote_plus(query)}"
            response = requests.get(search_url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search results (various possible structures)
                search_results = (
                    soup.find_all('article', limit=max_results) or
                    soup.find_all('div', class_='search-result', limit=max_results) or
                    soup.find_all('div', class_='result', limit=max_results) or
                    soup.find_all('li', class_='search-item', limit=max_results)
                )
                
                for result_elem in search_results:
                    try:
                        # Extract data from various possible structures
                        title_elem = (
                            result_elem.find('h2') or 
                            result_elem.find('h3') or 
                            result_elem.find('a', class_='title')
                        )
                        
                        link_elem = result_elem.find('a')
                        
                        snippet_elem = (
                            result_elem.find('p', class_='snippet') or
                            result_elem.find('p', class_='description') or
                            result_elem.find('p')
                        )
                        
                        if title_elem and link_elem:
                            href = link_elem.get('href', '')
                            if not href.startswith('http'):
                                href = f"{self.base_url}{href}"
                            
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': href,
                                'snippet': snippet_elem.get_text(strip=True)[:300] if snippet_elem else '',
                                'source': 'grokipedia',
                                'timestamp': datetime.now().isoformat()
                            })
                    except:
                        continue
                
                elapsed = time.time() - start_time
                print(f"✅ Found {len(results)} results in {elapsed:.2f}s")
                
        except Exception as e:
            print(f"❌ General search failed: {e}")
        
        return results
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract comprehensive content from article page
        Gets: title, summary, full content, metadata
        """
        article = {
            'url': url,
            'source': 'grokipedia',
            'timestamp': datetime.now().isoformat(),
            'verified': True,  # Grokipedia content is verified
        }
        
        # Extract title
        title_elem = (
            soup.find('h1', class_='title') or
            soup.find('h1') or
            soup.find('title')
        )
        article['title'] = title_elem.get_text(strip=True) if title_elem else 'Unknown'
        
        # Extract summary/intro (first paragraph)
        intro_elem = (
            soup.find('div', class_='intro') or
            soup.find('div', class_='summary') or
            soup.find('p', class_='lead')
        )
        
        if intro_elem:
            article['summary'] = intro_elem.get_text(strip=True)
        else:
            # Get first substantial paragraph
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 100:  # Substantial content
                    article['summary'] = text
                    break
        
        # Extract main content
        content_elem = (
            soup.find('article') or
            soup.find('div', class_='content') or
            soup.find('div', class_='article-body') or
            soup.find('main')
        )
        
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                unwanted.decompose()
            
            # Get all paragraphs
            paragraphs = content_elem.find_all('p')
            full_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            article['content'] = full_text
            article['content_length'] = len(full_text)
            
            # Extract sections/headings for structure
            sections = []
            for heading in content_elem.find_all(['h2', 'h3']):
                sections.append(heading.get_text(strip=True))
            article['sections'] = sections
        
        # Extract metadata
        last_updated = soup.find('time', class_='updated')
        if last_updated:
            article['last_updated'] = last_updated.get('datetime') or last_updated.get_text(strip=True)
        
        # Extract categories/tags
        categories = []
        for cat in soup.find_all('a', class_=['category', 'tag']):
            categories.append(cat.get_text(strip=True))
        if categories:
            article['categories'] = categories
        
        return article
    
    def deep_search(self, query: str) -> Dict:
        """
        Deep search with comprehensive analysis
        1. Try direct article first (fastest)
        2. If not found, do general search
        3. Extract full content from best match
        """
        start_time = time.time()
        print(f"\n🔬 Deep Search: {query}")
        print("=" * 60)
        
        # Try direct article first
        article = self.search_article(query)
        
        if article and article.get('content'):
            # Got full article directly
            total_time = time.time() - start_time
            print(f"✅ Deep search complete in {total_time:.2f}s")
            
            return {
                'query': query,
                'method': 'direct_article',
                'article': article,
                'search_time': f"{total_time:.2f}s",
                'success': True
            }
        else:
            # Need to do general search
            results = self.search_general(query, max_results=3)
            
            if results:
                # Get full content from top result
                top_result = results[0]
                print(f"\n📄 Fetching full content from: {top_result['title']}")
                
                try:
                    response = requests.get(top_result['url'], headers=self.get_headers(), timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        article = self._extract_article_content(soup, top_result['url'])
                        
                        total_time = time.time() - start_time
                        print(f"✅ Deep search complete in {total_time:.2f}s")
                        
                        return {
                            'query': query,
                            'method': 'search_then_fetch',
                            'article': article,
                            'alternative_results': results[1:],
                            'search_time': f"{total_time:.2f}s",
                            'success': True
                        }
                except Exception as e:
                    print(f"⚠️ Failed to fetch full content: {e}")
            
            total_time = time.time() - start_time
            return {
                'query': query,
                'method': 'search_only',
                'results': results,
                'search_time': f"{total_time:.2f}s",
                'success': len(results) > 0
            }


# Global instance
_grok_engine = None

def get_grok_engine():
    """Get or create Grokipedia engine"""
    global _grok_engine
    if _grok_engine is None:
        _grok_engine = GrokipediaEngine()
    return _grok_engine


# AI Tool Functions
def grokipedia_search(query: str) -> Dict:
    """
    AI Tool: Fast Grokipedia search
    Direct article access for verified, up-to-date information
    Target: <3 seconds
    """
    engine = get_grok_engine()
    article = engine.search_article(query)
    
    if article:
        return {
            'query': query,
            'found': True,
            'title': article.get('title'),
            'summary': article.get('summary', '')[:500],  # First 500 chars
            'url': article.get('url'),
            'verified': True,
            'search_time': article.get('search_time'),
            'source': 'grokipedia'
        }
    else:
        # Fallback to general search
        results = engine.search_general(query, max_results=3)
        return {
            'query': query,
            'found': len(results) > 0,
            'results': results[:3],
            'message': 'Found related articles' if results else 'No results found'
        }


def grokipedia_deep_research(query: str) -> Dict:
    """
    AI Tool: Deep Grokipedia research
    Comprehensive content extraction with full article text
    Target: <5 seconds
    """
    engine = get_grok_engine()
    return engine.deep_search(query)


if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Grokipedia-Focused Search System\n")
    
    test_queries = [
        "Artificial Intelligence",
        "Python programming language",
        "Quantum Computing",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"TEST: {query}")
        print('='*70)
        
        result = grokipedia_search(query)
        print(f"\n📊 Result:")
        print(f"  Found: {result.get('found')}")
        if result.get('found'):
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Time: {result.get('search_time', 'N/A')}")
            if result.get('summary'):
                print(f"  Summary: {result['summary'][:150]}...")
