#!/usr/bin/env python3
"""Test script for new tools (network, git, code)."""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_network_tools():
    """Test network tools."""
    print("\n" + "="*60)
    print("Testing Network Tools")
    print("="*60)
    
    try:
        from tools.network.network_tools import (
            ping, network_info, dns_lookup, check_port
        )
        
        # Test ping
        print("\n1. Testing ping...")
        result = ping("8.8.8.8", count=2)
        print(f"   ✓ Ping result: {result.get('success', False)}")
        
        # Test network_info
        print("\n2. Testing network_info...")
        result = network_info()
        print(f"   ✓ Hostname: {result.get('hostname', 'N/A')}")
        print(f"   ✓ Local IP: {result.get('local_ip', 'N/A')}")
        
        # Test DNS lookup
        print("\n3. Testing dns_lookup...")
        result = dns_lookup("google.com")
        print(f"   ✓ DNS lookup: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ IPs: {result.get('ip_addresses', [])}")
        
        # Test port check
        print("\n4. Testing check_port...")
        result = check_port("google.com", 443, timeout=3)
        print(f"   ✓ Port 443 status: {result.get('status', 'unknown')}")
        
        print("\n✅ Network tools test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Network tools test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_git_tools():
    """Test git tools."""
    print("\n" + "="*60)
    print("Testing Git Tools")
    print("="*60)
    
    try:
        from tools.git.git_tools import (
            git_status, git_log, git_current_branch, git_branch_list
        )
        
        repo_path = str(project_root)
        
        # Test git_current_branch
        print("\n1. Testing git_current_branch...")
        result = git_current_branch(repo_path)
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Branch: {result.get('branch', 'N/A')}")
        
        # Test git_status
        print("\n2. Testing git_status...")
        result = git_status(repo_path)
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Modified: {len(result.get('modified_files', []))}")
            print(f"   ✓ Untracked: {len(result.get('untracked_files', []))}")
        
        # Test git_log
        print("\n3. Testing git_log...")
        result = git_log(repo_path, max_count=3)
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Commits: {len(result.get('commits', []))}")
        
        # Test git_branch_list
        print("\n4. Testing git_branch_list...")
        result = git_branch_list(repo_path)
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Branches: {len(result.get('local_branches', []))}")
        
        print("\n✅ Git tools test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Git tools test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_code_tools():
    """Test code tools."""
    print("\n" + "="*60)
    print("Testing Code Tools")
    print("="*60)
    
    try:
        from tools.code.code_tools import (
            analyze_file, find_todos, count_lines, check_syntax
        )
        
        # Test analyze_file
        print("\n1. Testing analyze_file...")
        test_file = project_root / "tools" / "__init__.py"
        result = analyze_file(str(test_file))
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Lines: {result.get('total_lines', 0)}")
            print(f"   ✓ Functions: {result.get('function_count', 0)}")
        
        # Test check_syntax
        print("\n2. Testing check_syntax...")
        result = check_syntax(str(test_file))
        print(f"   ✓ Valid: {result.get('valid', False)}")
        
        # Test count_lines
        print("\n3. Testing count_lines...")
        tools_dir = project_root / "tools"
        result = count_lines(str(tools_dir), extensions=[".py"])
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ Total lines: {result.get('total_lines', 0)}")
            print(f"   ✓ Files: {result.get('file_count', 0)}")
        
        # Test find_todos
        print("\n4. Testing find_todos...")
        result = find_todos(str(tools_dir))
        print(f"   ✓ Success: {result.get('success', False)}")
        if result.get('success'):
            print(f"   ✓ TODOs found: {len(result.get('todos', []))}")
        
        print("\n✅ Code tools test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Code tools test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_registry():
    """Test that all new tools are registered."""
    print("\n" + "="*60)
    print("Testing Tool Registry")
    print("="*60)
    
    try:
        from tools import TOOLS
        
        # Check categories
        expected_categories = ["network", "git", "code"]
        for category in expected_categories:
            if category in TOOLS:
                print(f"   ✓ Category '{category}' registered")
                print(f"     Tools: {len(TOOLS[category])}")
            else:
                print(f"   ❌ Category '{category}' NOT registered")
                return False
        
        # Count total tools
        total = sum(len(tools) for tools in TOOLS.values())
        print(f"\n   ✓ Total tools registered: {total}")
        
        print("\n✅ Tool registry test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Tool registry test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 NEW TOOLS TEST SUITE")
    print("="*60)
    
    results = {
        "Network Tools": test_network_tools(),
        "Git Tools": test_git_tools(),
        "Code Tools": test_code_tools(),
        "Tool Registry": test_tool_registry()
    }
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
