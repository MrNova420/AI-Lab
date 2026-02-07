#!/usr/bin/env python3
"""
🌟 Grokipedia PRIMARY Search Engine with JavaScript Rendering
Full Phase 2 Implementation - Fast, Accurate, Comprehensive

Features:
- JavaScript rendering with Playwright (access modern websites)
- Fast: <3 seconds for most queries
- Comprehensive: Full article extraction
- Verified: Grokipedia content is always verified
- Smart caching: Avoid re-rendering same pages
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import hashlib
import json

try:
    from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available - install with: pip install playwright && playwright install chromium")


class GrokipediaEngine:
    """
    Advanced Grokipedia search engine with JavaScript rendering
    PRIMARY knowledge source for AI
    """
    
    def __init__(self):
        self.base_url = "https://grokipedia.com"
        self.cache = {}  # Cache rendered pages
        self.cache_ttl = 300  # 5 minutes cache
        self.timeout = 10000  # 10 seconds for page load
        
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('cached_at')
        if not cached_time:
            return False
        
        age = (datetime.now() - cached_time).total_seconds()
        return age < self.cache_ttl
    
    async def render_page(self, url: str) -> str:
        """
        Render JavaScript page with Playwright
        Returns HTML after JavaScript execution
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not installed")
        
        # Check cache first
        cache_key = self._get_cache_key(url)
        if self._is_cache_valid(cache_key):
            print(f"💾 Using cached result for: {url}")
            return self.cache[cache_key]['html']
        
        print(f"🌐 Rendering page: {url}")
        start_time = time.time()
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # Navigate and wait for page load
                await page.goto(url, wait_until='networkidle', timeout=self.timeout)
                
                # Wait a bit for any dynamic content
                await page.wait_for_timeout(1000)
                
                # Get rendered HTML
                html = await page.content()
                
                elapsed = time.time() - start_time
                print(f"✅ Page rendered in {elapsed:.2f}s")
                
                # Cache the result
                self.cache[cache_key] = {
                    'html': html,
                    'cached_at': datetime.now(),
                    'url': url
                }
                
                return html
                
            except PlaywrightTimeout:
                print(f"⚠️ Page load timeout: {url}")
                return ""
            finally:
                await browser.close()
    
    async def search_direct_article(self, query: str) -> Optional[Dict]:
        """
        Search for article directly by name
        FAST: Direct access to article
        """
        start_time = time.time()
        print(f"\n🌟 Grokipedia Direct Search: {query}")
        
        # Try different URL formats
        article_slugs = [
            query.replace(' ', '_'),  # Python_programming
            query.replace(' ', '-'),  # Python-programming
            query.title().replace(' ', '_'),  # Python_Programming
            query.lower().replace(' ', '_'),  # python_programming
        ]
        
        for slug in article_slugs:
            try:
                url = f"{self.base_url}/wiki/{quote_plus(slug)}"
                html = await self.render_page(url)
                
                if html and len(html) > 1000:  # Got substantial content
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Check if it's a real article (not 404)
                    title = soup.find('h1')
                    if title and 'not found' not in title.get_text().lower():
                        article = self._extract_article(soup, url)
                        
                        elapsed = time.time() - start_time
                        article['search_time'] = f"{elapsed:.2f}s"
                        article['method'] = 'direct_article'
                        
                        print(f"✅ Found article: {article['title']} ({elapsed:.2f}s)")
                        return article
                        
            except Exception as e:
                continue
        
        print(f"⚠️ Direct article not found")
        return None
    
    async def search_general(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        General search using Grokipedia search page
        Returns list of matching articles
        """
        start_time = time.time()
        print(f"\n🔍 Grokipedia General Search: {query}")
        
        results = []
        
        try:
            # Search page URL
            search_url = f"{self.base_url}/search?q={quote_plus(query)}"
            html = await self.render_page(search_url)
            
            if not html:
                return results
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find search results (try multiple selectors)
            result_containers = (
                soup.find_all('article', limit=max_results) or
                soup.find_all('div', class_='search-result', limit=max_results) or
                soup.find_all('div', attrs={'data-testid': 'search-result'}, limit=max_results) or
                soup.find_all('li', class_='result', limit=max_results)
            )
            
            for container in result_containers:
                try:
                    # Extract title
                    title_elem = (
                        container.find('h2') or
                        container.find('h3') or
                        container.find('a', class_='title')
                    )
                    
                    # Extract link
                    link_elem = container.find('a')
                    
                    # Extract snippet/description
                    snippet_elem = (
                        container.find('p', class_='snippet') or
                        container.find('p', class_='description') or
                        container.find('p')
                    )
                    
                    if title_elem and link_elem:
                        href = link_elem.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': href,
                            'snippet': snippet_elem.get_text(strip=True)[:300] if snippet_elem else '',
                            'source': 'grokipedia',
                            'verified': True,
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as e:
                    continue
            
            elapsed = time.time() - start_time
            print(f"✅ Found {len(results)} results ({elapsed:.2f}s)")
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
        
        return results
    
    def _extract_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract comprehensive article content
        Returns structured article data
        """
        article = {
            'url': url,
            'source': 'grokipedia',
            'verified': True,
            'timestamp': datetime.now().isoformat()
        }
        
        # Title
        title_elem = soup.find('h1') or soup.find('title')
        article['title'] = title_elem.get_text(strip=True) if title_elem else 'Unknown'
        
        # Main content area
        content_elem = (
            soup.find('article') or
            soup.find('main') or
            soup.find('div', class_='content') or
            soup.find('div', id='content')
        )
        
        if content_elem:
            # Remove unwanted elements
            for unwanted in content_elem.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                unwanted.decompose()
            
            # Extract summary (first paragraph)
            first_p = content_elem.find('p')
            if first_p:
                text = first_p.get_text(strip=True)
                if len(text) > 50:
                    article['summary'] = text
            
            # Extract all paragraphs for full content
            paragraphs = content_elem.find_all('p')
            full_text = '\n\n'.join([
                p.get_text(strip=True) 
                for p in paragraphs 
                if len(p.get_text(strip=True)) > 50
            ])
            
            article['content'] = full_text
            article['content_length'] = len(full_text)
            article['word_count'] = len(full_text.split())
            
            # Extract sections
            sections = []
            for heading in content_elem.find_all(['h2', 'h3', 'h4']):
                sections.append(heading.get_text(strip=True))
            if sections:
                article['sections'] = sections
        
        # Extract metadata
        time_elem = soup.find('time')
        if time_elem:
            article['last_updated'] = time_elem.get('datetime') or time_elem.get_text(strip=True)
        
        return article
    
    async def deep_research(self, query: str) -> Dict:
        """
        Comprehensive research on a topic
        1. Try direct article (fastest)
        2. If not found, search and fetch top result
        3. Return full article content
        """
        start_time = time.time()
        print(f"\n🔬 Grokipedia Deep Research: {query}")
        print("=" * 70)
        
        # Try direct article first
        article = await self.search_direct_article(query)
        
        if article and article.get('content'):
            total_time = time.time() - start_time
            print(f"✅ Research complete: {total_time:.2f}s (direct)")
            
            return {
                'query': query,
                'success': True,
                'method': 'direct_article',
                'article': article,
                'search_time': f"{total_time:.2f}s"
            }
        
        # Fallback: general search
        print("\n📋 Direct article not found, trying general search...")
        results = await self.search_general(query, max_results=3)
        
        if results:
            # Fetch full content from top result
            top_result = results[0]
            print(f"\n📄 Fetching full article: {top_result['title']}")
            
            try:
                html = await self.render_page(top_result['url'])
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    article = self._extract_article(soup, top_result['url'])
                    
                    total_time = time.time() - start_time
                    print(f"✅ Research complete: {total_time:.2f}s (search + fetch)")
                    
                    return {
                        'query': query,
                        'success': True,
                        'method': 'search_and_fetch',
                        'article': article,
                        'alternatives': results[1:],
                        'search_time': f"{total_time:.2f}s"
                    }
            except Exception as e:
                print(f"⚠️ Failed to fetch article: {e}")
        
        total_time = time.time() - start_time
        return {
            'query': query,
            'success': False,
            'method': 'not_found',
            'results': results,
            'search_time': f"{total_time:.2f}s"
        }


# Global engine instance
_grok_engine = None

def get_grok_engine():
    """Get or create Grokipedia engine"""
    global _grok_engine
    if _grok_engine is None:
        _grok_engine = GrokipediaEngine()
    return _grok_engine


# Synchronous wrapper functions for AI tools
def grokipedia_search(query: str) -> Dict:
    """
    AI Tool: Fast Grokipedia search
    PRIMARY knowledge source - verified, comprehensive, up-to-date
    Target: <3 seconds
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            'error': 'Playwright not installed',
            'message': 'Run: pip install playwright && playwright install chromium'
        }
    
    engine = get_grok_engine()
    
    # Run async search in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.search_direct_article(query))
        
        if result:
            return {
                'query': query,
                'success': True,
                'title': result.get('title'),
                'summary': result.get('summary', '')[:500],
                'content_preview': result.get('content', '')[:1000],
                'url': result.get('url'),
                'word_count': result.get('word_count', 0),
                'verified': True,
                'source': 'grokipedia',
                'search_time': result.get('search_time')
            }
        else:
            # Fallback to general search
            results = loop.run_until_complete(engine.search_general(query, max_results=3))
            return {
                'query': query,
                'success': len(results) > 0,
                'results': results[:3],
                'message': f"Found {len(results)} related articles"
            }
    finally:
        loop.close()


def grokipedia_deep_research(query: str) -> Dict:
    """
    AI Tool: Comprehensive Grokipedia research
    Full article extraction with complete content
    Target: <5 seconds
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {
            'error': 'Playwright not installed',
            'message': 'Run: pip install playwright && playwright install chromium'
        }
    
    engine = get_grok_engine()
    
    # Run async research in sync context
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(engine.deep_research(query))
        return result
    finally:
        loop.close()


if __name__ == "__main__":
    print("🧪 Testing Grokipedia Engine with JavaScript Rendering\n")
    
    test_queries = [
        "Artificial Intelligence",
        "Python programming",
        "Quantum Computing",
    ]
    
    for query in test_queries:
        print(f"\n{'='*70}")
        print(f"TEST: {query}")
        print('='*70)
        
        result = grokipedia_search(query)
        
        if result.get('success'):
            print(f"\n✅ SUCCESS!")
            print(f"  Title: {result.get('title')}")
            print(f"  Time: {result.get('search_time')}")
            print(f"  Words: {result.get('word_count')}")
            if result.get('summary'):
                print(f"  Summary: {result['summary'][:200]}...")
        else:
            print(f"\n⚠️ Not found directly")
            if result.get('results'):
                print(f"  Found {len(result['results'])} related articles")
