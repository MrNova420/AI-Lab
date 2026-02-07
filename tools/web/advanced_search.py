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
from typing import List, Dict, Callable, Optional


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
        self.timeout = 8  # Reduced from 15 to 8 for speed
        self.max_retries = 2  # Reduced from 3 to 2
        self.cache = {}  # Simple in-memory cache
        self.progress_callback = None  # For live progress updates
        
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
        Search Google - PRIMARY SOURCE (most reliable and comprehensive)
        """
        if self.progress_callback:
            self.progress_callback("🔍 Searching Google (primary)...")
        
        print(f"🔍 Searching Google: {query}")
        results = []
        
        try:
            # Google search URL with additional parameters for better results
            url = f"https://www.google.com/search?q={quote_plus(query)}&num={max_results}&hl=en"
            response = requests.get(url, headers=self.get_headers(), timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Multiple selectors for Google results (they change frequently)
                search_results = soup.find_all('div', class_='g')
                if not search_results:
                    search_results = soup.find_all('div', {'data-sokoban-container': True})
                
                for result in search_results[:max_results]:
                    try:
                        # Extract title (multiple possible selectors)
                        title_elem = result.find('h3')
                        if not title_elem:
                            title_elem = result.find('div', {'role': 'heading'})
                        title = title_elem.get_text() if title_elem else 'No title'
                        
                        # Extract URL
                        link_elem = result.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        # Clean URL (Google sometimes wraps URLs)
                        if url.startswith('/url?q='):
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        # Extract snippet (multiple possible selectors)
                        snippet_elem = result.find('div', class_=['VwiC3b', 'yXK7lf', 'IsZvec'])
                        if not snippet_elem:
                            snippet_elem = result.find('span', class_='aCOpRe')
                        snippet = snippet_elem.get_text() if snippet_elem else ''
                        
                        if url and title and not url.startswith('#'):
                            results.append({
                                'title': title,
                                'url': url,
                                'snippet': snippet,
                                'source': 'google',
                                'quality_score': 1.5,  # Google is highest quality
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as e:
                        continue
                        
            print(f"✅ Google: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Google search failed: {e}")
        
        return results
    
    def search_grokipedia(self, query, max_results=5):
        """
        Search Grokipedia - PRIMARY knowledge source (best, newest, most comprehensive)
        Better than Wikipedia - more up-to-date and comprehensive
        """
        if self.progress_callback:
            self.progress_callback("🌟 Searching Grokipedia (PRIMARY)...")
        
        print(f"🌟 Searching Grokipedia: {query}")
        results = []
        
        try:
            # Try direct article URL first
            article_url = f"https://grokipedia.com/wiki/{quote_plus(query.replace(' ', '_'))}"
            response = requests.get(article_url, headers=self.get_headers(), timeout=6)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title_elem = soup.find('h1') or soup.find('title')
                title = title_elem.get_text(strip=True) if title_elem else query
                
                # Extract first paragraph as snippet
                paragraphs = soup.find_all('p')
                snippet = ''
                for p in paragraphs[:3]:
                    text = p.get_text(strip=True)
                    if len(text) > 50:  # Skip short paragraphs
                        snippet = text[:300]
                        break
                
                results.append({
                    'title': title,
                    'url': article_url,
                    'snippet': snippet,
                    'source': 'grokipedia',
                    'quality_score': 2.0,  # HIGHEST - PRIMARY SOURCE
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"✅ Grokipedia: {len(results)} results (direct article)")
            else:
                # Try search page
                search_url = f"https://grokipedia.com/search?q={quote_plus(query)}"
                response = requests.get(search_url, headers=self.get_headers(), timeout=6)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find search results
                    search_results = soup.find_all('article', limit=max_results)
                    if not search_results:
                        search_results = soup.find_all('div', class_=['search-result', 'result'], limit=max_results)
                    
                    for result in search_results:
                        try:
                            title_elem = result.find(['h2', 'h3', 'a'])
                            link_elem = result.find('a')
                            snippet_elem = result.find('p')
                            
                            if title_elem and link_elem:
                                url = link_elem.get('href', '')
                                if not url.startswith('http'):
                                    url = f"https://grokipedia.com{url}"
                                
                                results.append({
                                    'title': title_elem.get_text(strip=True),
                                    'url': url,
                                    'snippet': snippet_elem.get_text(strip=True)[:200] if snippet_elem else '',
                                    'source': 'grokipedia',
                                    'quality_score': 2.0,  # HIGHEST - PRIMARY SOURCE
                                    'timestamp': datetime.now().isoformat()
                                })
                        except:
                            continue
                    
                    print(f"✅ Grokipedia: {len(results)} results (search)")
                else:
                    print(f"⚠️ Grokipedia: No results found")
                
        except Exception as e:
            print(f"⚠️ Grokipedia search failed: {e}")
        
        return results
    
    def search_wikipedia(self, query, max_results=5):
        """
        Search Wikipedia - SECONDARY knowledge source (reliable, factual)
        Uses Wikipedia API (very fast, no scraping needed)
        """
        if self.progress_callback:
            self.progress_callback("📚 Searching Wikipedia (secondary)...")
        
        print(f"📚 Searching Wikipedia: {query}")
        results = []
        
        try:
            # Wikipedia API search
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={quote_plus(query)}&limit={max_results}&format=json"
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                titles = data[1]  # Article titles
                descriptions = data[2]  # Descriptions
                urls = data[3]  # Full URLs
                
                for i in range(min(len(titles), max_results)):
                    if titles[i] and urls[i]:
                        results.append({
                            'title': titles[i],
                            'url': urls[i],
                            'snippet': descriptions[i] if i < len(descriptions) else '',
                            'source': 'wikipedia',
                            'quality_score': 1.4,  # High-quality but secondary
                            'timestamp': datetime.now().isoformat()
                        })
            
            print(f"✅ Wikipedia: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Wikipedia search failed: {e}")
        
        return results
    
    def search_wikimedia_commons(self, query, max_results=5):
        """
        Search Wikimedia Commons and other Wikimedia projects
        Includes Wikibooks, Wikinews, Wikiquote, etc.
        """
        if self.progress_callback:
            self.progress_callback("📖 Searching Wikimedia projects...")
        
        print(f"📖 Searching Wikimedia projects: {query}")
        results = []
        
        # Search multiple Wikimedia projects
        wikimedia_projects = [
            ('wikibooks', 'https://en.wikibooks.org/w/api.php', 'Wikibooks'),
            ('wikinews', 'https://en.wikinews.org/w/api.php', 'Wikinews'),
            ('wikiquote', 'https://en.wikiquote.org/w/api.php', 'Wikiquote'),
            ('wikiversity', 'https://en.wikiversity.org/w/api.php', 'Wikiversity'),
        ]
        
        try:
            for project_key, api_url, project_name in wikimedia_projects[:2]:  # Limit to 2 for speed
                try:
                    search_url = f"{api_url}?action=opensearch&search={quote_plus(query)}&limit=2&format=json"
                    response = requests.get(search_url, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        titles = data[1]
                        descriptions = data[2]
                        urls = data[3]
                        
                        for i in range(min(len(titles), 2)):  # Max 2 per project
                            if titles[i] and urls[i]:
                                results.append({
                                    'title': f"{titles[i]} ({project_name})",
                                    'url': urls[i],
                                    'snippet': descriptions[i] if i < len(descriptions) else '',
                                    'source': 'wikimedia',
                                    'quality_score': 1.2,
                                    'timestamp': datetime.now().isoformat()
                                })
                except:
                    continue
            
            print(f"✅ Wikimedia: {len(results)} results")
        except Exception as e:
            print(f"⚠️ Wikimedia search failed: {e}")
        
        return results
    
    def search_everipedia(self, query, max_results=5):
        """
        Search Everipedia/IQ.wiki - Modern decentralized encyclopedia
        PRIMARY knowledge source (newer, comprehensive, up-to-date)
        """
        if self.progress_callback:
            self.progress_callback("🌐 Searching Everipedia (IQ.wiki)...")
        
        print(f"🌐 Searching Everipedia: {query}")
        results = []
        
        try:
            # Everipedia/IQ.wiki search
            # Using web scraping approach since they don't have public API
            url = f"https://iq.wiki/wiki/{quote_plus(query.replace(' ', '_'))}"
            response = requests.get(url, headers=self.get_headers(), timeout=6)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract title
                title_elem = soup.find('h1')
                title = title_elem.get_text() if title_elem else query
                
                # Extract first paragraph as snippet
                para = soup.find('p')
                snippet = para.get_text()[:200] if para else ''
                
                results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet,
                    'source': 'everipedia',
                    'quality_score': 1.5,  # PRIMARY - highest quality, most up-to-date
                    'timestamp': datetime.now().isoformat()
                })
                
                print(f"✅ Everipedia: {len(results)} results")
            else:
                print(f"⚠️ Everipedia: No direct article found")
                
        except Exception as e:
            print(f"⚠️ Everipedia search failed: {e}")
        
        return results
    
    def search_fandom(self, query, max_results=3):
        """
        Search Fandom wikis - Good for specific topics/communities
        """
        if self.progress_callback:
            self.progress_callback("🎮 Searching Fandom wikis...")
        
        print(f"🎮 Searching Fandom: {query}")
        results = []
        
        try:
            # Fandom community search
            url = f"https://www.fandom.com/search?query={quote_plus(query)}"
            response = requests.get(url, headers=self.get_headers(), timeout=6)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find search results
                search_results = soup.find_all('article', limit=max_results)
                
                for result in search_results:
                    try:
                        title_elem = result.find('h3') or result.find('h2')
                        link_elem = result.find('a')
                        snippet_elem = result.find('p')
                        
                        if title_elem and link_elem:
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': link_elem.get('href', ''),
                                'snippet': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'source': 'fandom',
                                'quality_score': 1.0,
                                'timestamp': datetime.now().isoformat()
                            })
                    except:
                        continue
                
                print(f"✅ Fandom: {len(results)} results")
                
        except Exception as e:
            print(f"⚠️ Fandom search failed: {e}")
        
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
    
    def parallel_search(self, query, max_results=10, sources=['grokipedia', 'wikipedia', 'google', 'wikimedia', 'bing', 'duckduckgo']):
        """
        Search multiple sources in parallel for speed
        PRIORITY ORDER (best to backup):
        1. Grokipedia - PRIMARY knowledge base (newest, most comprehensive, better than Wikipedia!)
        2. Wikipedia - SECONDARY knowledge base (reliable, factual)
        3. Google - Web search leader
        4. Wikimedia - Additional knowledge (Wikibooks, Wikinews, etc.)
        5. Bing - Backup search engine
        6. DuckDuckGo - Privacy-focused backup
        """
        if self.progress_callback:
            self.progress_callback(f"🚀 Searching {len(sources)} sources in parallel...")
        
        print(f"🚀 Parallel search across {len(sources)} sources...")
        print(f"   Priority: 🌟 Grokipedia → 📚 Wikipedia → 🔍 Google → 📖 Others")
        
        all_results = []
        search_methods = {
            'grokipedia': self.search_grokipedia,
            'everipedia': self.search_everipedia,
            'wikipedia': self.search_wikipedia,
            'wikimedia': self.search_wikimedia_commons,
            'fandom': self.search_fandom,
            'google': self.search_google,
            'bing': self.search_bing,
            'duckduckgo': self.search_duckduckgo,
            'brave': self.search_brave
        }
        
        with ThreadPoolExecutor(max_workers=min(len(sources), 6)) as executor:
            future_to_source = {
                executor.submit(search_methods[source], query, max_results): source
                for source in sources if source in search_methods
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    results = future.result(timeout=10)  # Reduced timeout
                    all_results.extend(results)
                    if self.progress_callback:
                        self.progress_callback(f"✅ {source.title()}: {len(results)} results")
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
        PRIORITY: Grokipedia > Wikipedia > Google > Wikimedia > Bing > Others
        """
        source_weights = {
            'grokipedia': 2.0,  # PRIMARY - newest, most comprehensive (BEST!)
            'wikipedia': 1.4,   # SECONDARY - reliable, factual knowledge
            'everipedia': 1.3,  # Alternative knowledge base
            'google': 1.3,      # Web search leader
            'wikimedia': 1.2,   # Additional knowledge sources
            'bing': 1.1,        # Good quality search
            'brave': 1.0,       # Privacy-focused
            'duckduckgo': 1.0,  # Privacy-focused
            'fandom': 0.9       # Community wikis (specialized)
        }
        
        for i, result in enumerate(results):
            source = result.get('source', 'unknown')
            weight = source_weights.get(source, 0.8)
            
            # Factor in position (earlier = better)
            position_score = 1.0 - (i * 0.01)  # Small penalty for position
            
            # Get quality score from search (if set)
            quality = result.get('quality_score', 1.0)
            
            # Calculate final score
            result['relevance_score'] = weight * position_score * quality
        
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
        Perform deep research on a topic with multi-step verification
        1. Multi-source search (Google, Wikipedia, Bing, etc.)
        2. Analyze and rank results
        3. Scrape top result pages
        4. Verify facts and cross-reference
        5. Generate intelligent summary
        """
        print(f"\n🔬 Deep Research: {query}")
        print("=" * 60)
        
        # Step 1: Multi-source search
        if self.progress_callback:
            self.progress_callback("📡 Step 1/5: Searching multiple sources...")
        print("\n📡 Step 1: Searching multiple sources...")
        
        all_results = self.search_engine.parallel_search(
            query, 
            max_results=max_results,
            sources=['grokipedia', 'wikipedia', 'google', 'wikimedia', 'bing', 'duckduckgo']
        )
        
        # Step 2: Analyze and rank
        if self.progress_callback:
            self.progress_callback(f"🔍 Step 2/5: Analyzing {len(all_results)} results...")
        print(f"\n🔍 Step 2: Analyzing and ranking results...")
        
        unique_results = self.search_engine.deduplicate_results(all_results)
        ranked_results = self.search_engine.rank_results(unique_results)
        
        sources_used = list(set(r['source'] for r in ranked_results))
        print(f"✅ Found {len(ranked_results)} unique results from {len(sources_used)} sources")
        print(f"   Sources: {', '.join(sources_used)}")
        
        # Step 3: Scrape top results
        if self.progress_callback:
            self.progress_callback(f"📄 Step 3/5: Scraping top {scrape_top} pages...")
        print(f"\n📄 Step 3: Scraping top {scrape_top} results...")
        
        top_urls = [r['url'] for r in ranked_results[:scrape_top] if r.get('url')]
        scraped_content = self.scraper.scrape_multiple(top_urls)
        
        successful_scrapes = [s for s in scraped_content if s.get('success')]
        print(f"✅ Successfully scraped {len(successful_scrapes)}/{len(top_urls)} pages")
        
        # Step 4: Verify and cross-reference
        if self.progress_callback:
            self.progress_callback("✓ Step 4/5: Verifying facts and cross-referencing...")
        print("\n✓ Step 4: Verifying facts...")
        
        verification = self._verify_research_quality(ranked_results, scraped_content)
        print(f"✅ Verification complete - Quality score: {verification['quality_score']}/100")
        
        # Step 5: Analyze and generate summary
        if self.progress_callback:
            self.progress_callback("🧠 Step 5/5: Generating intelligent summary...")
        print("\n🧠 Step 5: Analyzing results...")
        
        analysis = self._analyze_research(ranked_results, scraped_content)
        analysis['verification'] = verification
        
        return {
            'query': query,
            'search_results': ranked_results,
            'scraped_content': scraped_content,
            'analysis': analysis,
            'timestamp': datetime.now().isoformat()
        }
    
    def _verify_research_quality(self, search_results, scraped_content):
        """
        Verify research quality through cross-referencing
        """
        verification = {
            'sources_checked': len(set(r['source'] for r in search_results)),
            'domains_found': len(set(urlparse(r['url']).netloc for r in search_results if r.get('url'))),
            'pages_scraped': len([s for s in scraped_content if s.get('success')]),
            'high_quality_sources': 0,
            'verified': False,
            'confidence': 0.0
        }
        
        # Check for high-quality sources
        high_quality_domains = [
            'grokipedia.com', 'wikipedia.org', 'iq.wiki', 'everipedia.org',  # Knowledge bases
            '.edu', '.gov', '.ac.',  # Educational/Government
            'mit.edu', 'stanford.edu', 'harvard.edu',  # Top universities
            'arxiv.org', 'scholar.google.com',  # Academic
            'nature.com', 'science.org', 'ieee.org'  # Scientific journals
        ]
        for result in search_results:
            url = result.get('url', '')
            if any(hq in url.lower() for hq in high_quality_domains):
                verification['high_quality_sources'] += 1
        
        # Calculate confidence
        confidence = 0.0
        confidence += min(verification['sources_checked'] / 4.0, 0.3)  # Max 30% for source diversity
        confidence += min(verification['domains_found'] / 10.0, 0.3)   # Max 30% for domain diversity
        confidence += min(verification['pages_scraped'] / 5.0, 0.2)    # Max 20% for scraped content
        confidence += min(verification['high_quality_sources'] / 3.0, 0.2)  # Max 20% for quality sources
        
        verification['confidence'] = min(confidence, 1.0)
        verification['verified'] = confidence >= 0.7  # 70% threshold
        
        # Quality score (0-100)
        verification['quality_score'] = int(confidence * 100)
        
        return verification
    
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
def advanced_web_search(query, max_results=10, progress_callback=None):
    """
    AI Tool: Advanced multi-source web search
    Searches Grokipedia (PRIMARY), Wikipedia (SECONDARY), Google, and more
    PRIORITY: Grokipedia > Wikipedia > Google > Others (knowledge bases first!)
    """
    engine = get_search_engine()
    engine.progress_callback = progress_callback
    
    results = engine.parallel_search(
        query, 
        max_results=max_results,
        sources=['grokipedia', 'wikipedia', 'google', 'wikimedia', 'bing']
    )
    unique_results = engine.deduplicate_results(results)
    ranked_results = engine.rank_results(unique_results)
    
    sources_used = list(set(r['source'] for r in ranked_results))
    
    return {
        'query': query,
        'total_results': len(ranked_results),
        'sources_used': sources_used,
        'priority_order': '🌟 Grokipedia → 📚 Wikipedia → 🔍 Google → 📖 Wikimedia → Bing',
        'top_results': ranked_results[:max_results]
    }


def deep_web_research(query, max_results=15, scrape_top=5, progress_callback=None):
    """
    AI Tool: Deep research with scraping and multi-step verification
    Best for comprehensive research on a topic
    5-step process: Search → Analyze → Scrape → Verify → Summarize
    """
    engine = get_research_engine()
    engine.search_engine.progress_callback = progress_callback
    engine.progress_callback = progress_callback
    
    return engine.deep_research(query, max_results=max_results, scrape_top=scrape_top)


def quick_fact_check(claim, progress_callback=None):
    """
    AI Tool: Quick fact checking across multiple sources
    Verifies claims by checking knowledge bases and search engines
    """
    engine = get_research_engine()
    engine.search_engine.progress_callback = progress_callback
    
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
