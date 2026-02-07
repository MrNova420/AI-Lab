#!/usr/bin/env python3
"""
Test Advanced Web Search System
"""

import sys
sys.path.insert(0, '/home/mrnova420/ai-forge')

from tools.web.advanced_search import (
    advanced_web_search,
    deep_web_research,
    quick_fact_check,
    scrape_webpage
)

def test_basic_search():
    """Test basic multi-source search"""
    print("\n" + "="*70)
    print("TEST 1: Basic Multi-Source Search")
    print("="*70)
    
    result = advanced_web_search("latest AI news 2026", max_results=5)
    
    print(f"\n📊 Results:")
    print(f"  Query: {result['query']}")
    print(f"  Total Results: {result['total_results']}")
    print(f"  Sources Used: {', '.join(result['sources_used'])}")
    print(f"\n🔝 Top Results:")
    
    for i, r in enumerate(result['top_results'][:3], 1):
        print(f"\n  {i}. {r['title']}")
        print(f"     URL: {r['url']}")
        print(f"     Source: {r['source']}")
        print(f"     Snippet: {r['snippet'][:100]}...")
    
    return len(result['top_results']) > 0

def test_fact_check():
    """Test fact checking"""
    print("\n" + "="*70)
    print("TEST 2: Fact Checking")
    print("="*70)
    
    result = quick_fact_check("Python is a programming language")
    
    print(f"\n📊 Results:")
    print(f"  Claim: {result['query']}")
    print(f"  Results Found: {result['results_found']}")
    print(f"  Sources Checked: {result['sources_checked']}")
    print(f"  Domains Found: {result['domains_found']}")
    print(f"  ✓ Verified: {result['verified']}")
    
    return result['verified']

def test_scraping():
    """Test webpage scraping"""
    print("\n" + "="*70)
    print("TEST 3: Webpage Scraping")
    print("="*70)
    
    result = scrape_webpage("https://www.python.org")
    
    print(f"\n📊 Results:")
    print(f"  URL: {result.get('url', 'N/A')}")
    print(f"  Title: {result.get('title', 'N/A')}")
    print(f"  Success: {result.get('success', False)}")
    
    if result.get('success'):
        content = result.get('content', '')
        print(f"  Content Length: {len(content)} chars")
        print(f"  Preview: {content[:200]}...")
        return True
    else:
        print(f"  Error: {result.get('error', 'Unknown')}")
        return False

def main():
    """Run all tests"""
    print("\n🧪 Testing Advanced Web Search System")
    print("="*70)
    
    tests = [
        ("Multi-Source Search", test_basic_search),
        ("Fact Checking", test_fact_check),
        ("Webpage Scraping", test_scraping)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed")

if __name__ == "__main__":
    main()
