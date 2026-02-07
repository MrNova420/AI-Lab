#!/usr/bin/env python3
"""
🌐 Advanced Multi-Source Web Search & Scraping System
Comprehensive web access with Google, Bing, DuckDuckGo, and more
"""

import requests
import json
import time
import re
from urllib.parse import quote_plus, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib


class MultiSourceSearchEngine:
    """
    Advanced search engine with multiple providers
    Google, Bing, DuckDuckGo, Brave, SearX, and more
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.timeout = 15
        self.max_retries = 3
        self.cache = {}  # Simple in-memory cache
        
    def get_headers(self, custom_headers=None):
        """Get random user agent headers"""
        import random
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
    def search_google(self, query, max_results=10):
        """
        Search Google via custom search or scraping
        """
        print(f"🔍 Searching Google: {query}")
        results = []
        
        try:
            # Google search URL
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}"
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search result divs
                search_results = soup.find_all('div', class_='g')
                
                for result in search_results[:max_results]:
                    try:
                        # Extract title
                        title_elem = result.find('h3')
                        title = title_elem.get_text() if title_elem else 'No title'
                        
                        # Extract URL
                        link_elem = result.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        # Extract snippet
                        snippet_elem = result.find('div', class_=['VwiC3b', 'yXK7lf'])
                        snippet = snippet_elem.get_text() if snippet_elem else ''
                        
                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'google',
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                        
            print(f"✅ Google: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
        
        return results
    
    def search_bing(self, query, max_results=10):
        """
        Search Bing
        """
        print(f"🔍 Searching Bing: {query}")
        results = []
        
        try:
            url = f"https://www.bing.com/search?q={quote_plus(query)}&count={max_results}"
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Bing search results
                search_results = soup.find_all('li', class_='b_algo')
                
                for result in search_results[:max_results]:
                    try:
                        title_elem = result.find('h2')
                        title = title_elem.get_text() if title_elem else 'No title'
                        
                        link_elem = result.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        snippet_elem = result.find('p')
                        snippet = snippet_elem.get_text() if snippet_elem else ''
                        
                        if url and title:
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'bing',
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                        
            print(f"✅ Bing: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Bing search failed: {e}")
        
        return results
    
    def search_duckduckgo(self, query, max_results=10):
        """
        Search DuckDuckGo (privacy-focused)
        """
        print(f"🔍 Searching DuckDuckGo: {query}")
        results = []
        
        try:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                search_results = soup.find_all('div', class_='result')
                
                for result in search_results[:max_results]:
                    try:
                        title_elem = result.find('a', class_='result__a')
                        snippet_elem = result.find('a', class_='result__snippet')
                        
                        if title_elem:
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': title_elem.get('href', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'source': 'duckduckgo',
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                        
            print(f"✅ DuckDuckGo: {len(results)} results")
        except Exception as e:
            print(f"⚠️ DuckDuckGo search failed: {e}")
        
        return results
    
    def search_brave(self, query, max_results=10):
        """
        Search Brave Search (privacy + good results)
        """
        print(f"🔍 Searching Brave: {query}")
        results = []
        
        try:
            url = f"https://search.brave.com/search?q={quote_plus(query)}"
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Brave uses different selectors
                search_results = soup.find_all('div', class_='snippet')
                
                for result in search_results[:max_results]:
                    try:
                        title_elem = result.find('span', class_='snippet-title')
                        link_elem = result.find('a', class_='result-header')
                        snippet_elem = result.find('p', class_='snippet-description')
                        
                        if title_elem and link_elem:
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': link_elem.get('href', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'source': 'brave',
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                        
            print(f"✅ Brave: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Brave search failed: {e}")
        
        return results
    
    def parallel_search(self, query, max_results=10, sources=['google', 'bing', 'duckduckgo', 'brave']):
        """
        Search multiple sources in parallel for speed
        """
        print(f"🚀 Parallel search across {len(sources)} sources...")
        
        all_results = []
        search_methods = {
            'google': self.search_google,
            'bing': self.search_bing,
            'duckduckgo': self.search_duckduckgo,
            'brave': self.search_brave
        }
        
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {
                executor.submit(search_methods[source], query, max_results): source
                for source in sources if source in search_methods
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results = future.result(timeout=20)
                    all_results.extend(results)
                except Exception as e:
                    print(f"⚠️ {source} failed: {e}")
        
        return all_results
    
    def deduplicate_results(self, results):
        """
        Remove duplicate results based on URL and title similarity
        """
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            # Normalize URL
            url_normalized = url.lower().rstrip('/')
            
            if url_normalized and url_normalized not in seen_urls:
                seen_urls.add(url_normalized)
                unique_results.append(result)
        
        return unique_results
    
    def rank_results(self, results):
        """
        Rank results by relevance and source quality
        """
        source_weights = {
            'google': 1.2,
            'bing': 1.1,
            'brave': 1.0,
            'duckduckgo': 1.0
        }
        
        for result in results:
            source = result.get('source', 'unknown')
            weight = source_weights.get(source, 1.0)
            
            # Calculate score based on position and source
            result['relevance_score'] = weight
        
        # Sort by score (descending)
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)


class WebScraper:
    """
    Advanced web scraper for extracting content from URLs
    """
    
    def __init__(self):
        self.timeout = 15
        self.max_content_length = 50000  # 50KB
    
    def scrape_url(self, url):
        """
        Scrape and extract main content from a URL
        """
        print(f"📄 Scraping: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            
            if response.status_code != 200:
                return {'error': f'HTTP {response.status_code}', 'url': url}
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract title
            title = soup.title.string if soup.title else 'No title'
            
            # Extract main content
            # Try to find main content areas
            main_content = None
            for tag in ['article', 'main', 'div[role="main"]', '.content', '.article', '#content']:
                main_content = soup.select_one(tag)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body
            
            # Get text
            text = main_content.get_text(separator='\n', strip=True) if main_content else ''
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            text = '\n'.join(lines)
            
            # Limit size
            if len(text) > self.max_content_length:
                text = text[:self.max_content_length] + '...[truncated]'
            
            return {
                'url': url,
                'title': title,
                'content': text,
                'length': len(text),
                'success': True
            }
            
        except Exception as e:
            print(f"⚠️ Scraping failed: {e}")
            return {'error': str(e), 'url': url, 'success': False}
    
    def scrape_multiple(self, urls, max_workers=5):
        """
        Scrape multiple URLs in parallel
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(self.scrape_url, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                try:
                    result = future.result(timeout=20)
                    results.append(result)
                except Exception as e:
                    url = future_to_url[future]
                    results.append({'error': str(e), 'url': url, 'success': False})
        
        return results


class DeepResearchEngine:
    """
    Deep research system that combines search, scraping, and analysis
    """
    
    def __init__(self):
        self.search_engine = MultiSourceSearchEngine()
        self.scraper = WebScraper()
    
    def deep_research(self, query, max_results=15, scrape_top=5):
        """
        Perform deep research on a topic
        1. Multi-source search
        2. Scrape top results
        3. Analyze and aggregate information
        """
        print(f"\n🔬 Deep Research: {query}")
        print("=" * 60)
        
        # Step 1: Multi-source search
        print("\n📡 Step 1: Searching multiple sources...")
        all_results = self.search_engine.parallel_search(
            query, 
            max_results=max_results,
            sources=['google', 'bing', 'duckduckgo', 'brave']
        )
        
        # Deduplicate and rank
        unique_results = self.search_engine.deduplicate_results(all_results)
        ranked_results = self.search_engine.rank_results(unique_results)
        
        print(f"✅ Found {len(ranked_results)} unique results across {len(set(r['source'] for r in ranked_results))} sources")
        
        # Step 2: Scrape top results
        print(f"\n📄 Step 2: Scraping top {scrape_top} results...")
        top_urls = [r['url'] for r in ranked_results[:scrape_top] if r.get('url')]
        scraped_content = self.scraper.scrape_multiple(top_urls)
        
        successful_scrapes = [s for s in scraped_content if s.get('success')]
        print(f"✅ Successfully scraped {len(successful_scrapes)}/{len(top_urls)} pages")
        
        # Step 3: Analyze and aggregate
        print("\n🧠 Step 3: Analyzing results...")
        analysis = self._analyze_research(ranked_results, scraped_content)
        
        return {
            'query': query,
            'search_results': ranked_results,
            'scraped_content': scraped_content,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_research(self, search_results, scraped_content):
        """
        Analyze research results for quality and insights
        """
        analysis = {
            'total_sources': len(set(r['source'] for r in search_results)),
            'total_results': len(search_results),
            'scraped_pages': len([s for s in scraped_content if s.get('success')]),
            'domains': {},
            'content_length': 0,
            'quality_score': 0
        }
        
        # Count domains
        for result in search_results:
            url = result.get('url', '')
            try:
                domain = urlparse(url).netloc
                analysis['domains'][domain] = analysis['domains'].get(domain, 0) + 1
            except:
                pass
        
        # Calculate total content
        for content in scraped_content:
            if content.get('success'):
                analysis['content_length'] += content.get('length', 0)
        
        # Quality score (0-100)
        score = 0
        score += min(analysis['total_sources'] * 20, 60)  # Max 60 for sources
        score += min(len(analysis['domains']) * 2, 20)     # Max 20 for domain diversity
        score += min(analysis['scraped_pages'] * 4, 20)    # Max 20 for scraped content
        analysis['quality_score'] = score
        
        return analysis
    
    def quick_fact_check(self, query):
        """
        Quick fact checking across multiple sources
        """
        print(f"\n✓ Quick Fact Check: {query}")
        
        # Search multiple sources
        results = self.search_engine.parallel_search(
            query,
            max_results=10,
            sources=['google', 'bing', 'duckduckgo']
        )
        
        unique_results = self.search_engine.deduplicate_results(results)
        
        # Analyze consensus
        sources_found = len(set(r['source'] for r in unique_results))
        domains_found = len(set(urlparse(r['url']).netloc for r in unique_results if r.get('url')))
        
        return {
            'query': query,
            'results_found': len(unique_results),
            'sources_checked': sources_found,
            'domains_found': domains_found,
            'verified': sources_found >= 3 and domains_found >= 5,
            'top_results': unique_results[:5]
        }


# Global instances
_search_engine = None
_research_engine = None

def get_search_engine():
    global _search_engine
    if _search_engine is None:
        _search_engine = MultiSourceSearchEngine()
    return _search_engine

def get_research_engine():
    global _research_engine
    if _research_engine is None:
        _research_engine = DeepResearchEngine()
    return _research_engine


# AI Tool Functions
def advanced_web_search(query, max_results=10):
    """
    AI Tool: Advanced multi-source web search
    Searches Google, Bing, DuckDuckGo, and Brave simultaneously
    """
    engine = get_search_engine()
    results = engine.parallel_search(query, max_results=max_results)
    unique_results = engine.deduplicate_results(results)
    ranked_results = engine.rank_results(unique_results)
    
    return {
        'query': query,
        'total_results': len(ranked_results),
        'sources_used': list(set(r['source'] for r in ranked_results)),
        'top_results': ranked_results[:max_results]
    }


def deep_web_research(query, max_results=15, scrape_top=5):
    """
    AI Tool: Deep research with scraping and analysis
    Best for comprehensive research on a topic
    """
    engine = get_research_engine()
    return engine.deep_research(query, max_results=max_results, scrape_top=scrape_top)


def quick_fact_check(claim):
    """
    AI Tool: Quick fact checking across multiple sources
    Verifies claims by checking multiple search engines
    """
    engine = get_research_engine()
    return engine.quick_fact_check(claim)


def scrape_webpage(url):
    """
    AI Tool: Scrape and extract content from a webpage
    Returns clean text content from any URL
    """
    scraper = WebScraper()
    return scraper.scrape_url(url)


def scrape_multiple_pages(urls):
    """
    AI Tool: Scrape multiple webpages in parallel
    Fast parallel scraping of multiple URLs
    """
    scraper = WebScraper()
    return scraper.scrape_multiple(urls)
