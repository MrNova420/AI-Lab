# 🌐 Web Search Priority System

## Priority Order (Best to Backup)

### 🥇 PRIMARY: Knowledge Bases
1. **Everipedia (IQ.wiki)** - Weight: 1.6
   - Newest, most comprehensive knowledge base
   - Decentralized, community-driven
   - More up-to-date than Wikipedia
   - Direct article access
   
2. **Wikipedia** - Weight: 1.4
   - Reliable, factual, well-maintained
   - Fast API access (no scraping)
   - Massive coverage
   - Secondary knowledge source

3. **Wikimedia Projects** - Weight: 1.2
   - Wikibooks, Wikinews, Wikiquote, Wikiversity
   - Specialized knowledge domains
   - Additional context and sources

### 🥈 SECONDARY: Search Engines  
4. **Google** - Weight: 1.3
   - Web search leader
   - Most comprehensive indexing
   - Best for current events and general web

5. **Bing** - Weight: 1.1
   - High success rate (90%+)
   - Good quality results
   - Reliable backup

6. **DuckDuckGo** - Weight: 1.0
   - Privacy-focused
   - No tracking
   - Good for sensitive searches

### 🥉 TERTIARY: Specialized
7. **Fandom** - Weight: 0.9
   - Community wikis
   - Specialized topics (gaming, TV, movies)
   - Good for pop culture

## Why This Order?

### Knowledge Bases First
- **Factual and Verified**: Everipedia and Wikipedia have editorial processes
- **Structured Data**: Better organized than random web pages
- **Fast Access**: APIs available, no heavy scraping needed
- **Up-to-date**: Everipedia especially focuses on current information
- **Comprehensive**: Cover wide range of topics in depth

### Search Engines Second
- **Current Events**: Better for breaking news
- **General Web**: Access to all websites
- **Broader Coverage**: Not limited to encyclopedic content
- **Multiple Perspectives**: Various sources and opinions

## Performance

### Speed
- **Everipedia**: 2-6 seconds (direct article access)
- **Wikipedia API**: 1-3 seconds (fastest!)
- **Google**: 3-8 seconds (scraping)
- **Bing**: 2-5 seconds (scraping)
- **Parallel Total**: 3-10 seconds for all sources

### Success Rates
- ✅ Wikipedia API: ~95% (most reliable)
- ✅ Everipedia: ~70% (good for known topics)
- ✅ Bing: ~90% (very reliable)
- ⚠️ Google: ~60-70% (anti-bot measures)
- ⚠️ Wikimedia: ~40-50% (smaller databases)

### Quality Scores
Results are ranked by:
1. Source weight (Everipedia 1.6 > Wikipedia 1.4 > Google 1.3, etc.)
2. Position score (earlier results = better)
3. Quality score (set by each search engine)

**Final Score = Source Weight × Position × Quality**

## Use Cases

### Use Everipedia + Wikipedia when:
- Looking for factual information
- Need verified, reliable sources
- Want encyclopedic content
- Researching established topics

### Add Google when:
- Need current events
- Want multiple perspectives
- Looking for specific websites
- Searching for non-encyclopedic content

### Add Bing/DuckDuckGo when:
- Want backup sources
- Need additional results
- Privacy concerns (DuckDuckGo)
- Diversifying search coverage

## Examples

### Query: "Python programming language"
**Results:**
1. 🥇 Everipedia: Python (programming language) - Score: 2.40
2. 🥇 Wikipedia: Python (programming language) - Score: 2.24
3. 🥈 Google: Python.org official site - Score: 1.95

### Query: "Latest AI news 2026"
**Results:**
1. 🥈 Google: TechCrunch - AI Breakthrough - Score: 1.95
2. 🥈 Bing: MIT News - AI Research - Score: 1.65
3. 🥇 Wikipedia: Artificial Intelligence - Score: 2.10 (background)

## Configuration

Default search order in `advanced_search.py`:
```python
sources=['everipedia', 'wikipedia', 'google', 'wikimedia', 'bing', 'duckduckgo']
```

Can be customized per query:
```python
advanced_web_search(
    query="...",
    sources=['wikipedia', 'google']  # Only these two
)
```

## Benefits

### For Users:
- ✅ Most reliable information first
- ✅ Faster responses (knowledge bases are quick)
- ✅ Better quality results
- ✅ Verified facts before opinions

### For AI:
- ✅ Structured, factual data first
- ✅ Easier to process and understand
- ✅ Higher confidence in responses
- ✅ Better citations and sources

## Future Enhancements

- [ ] Add more knowledge bases (Britannica, Scholarpedia)
- [ ] Academic search (Google Scholar, arXiv, PubMed)
- [ ] News-specific sources (Reuters, AP, BBC)
- [ ] Domain-specific wikis (medical, legal, technical)
- [ ] Real-time source health monitoring
- [ ] Dynamic priority adjustment based on query type
