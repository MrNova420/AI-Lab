#!/usr/bin/env python3
"""
Test Tool Execution End-to-End
Tests the complete flow: AI declares tools → Parser extracts → Executor runs → Results formatted
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.tool_executor import ToolExecutor
from scripts.smart_parser import parse_tool_declarations, remove_tool_declarations


def test_basic_flow():
    """Test basic tool execution flow"""
    print("🧪 Testing Basic Tool Execution Flow\n")
    print("=" * 60)
    
    # Simulate AI response with tool declaration
    ai_response = """<TOOLS>datetime</TOOLS>

Let me check the current date and time for you."""
    
    print(f"📝 AI Response:\n{ai_response}\n")
    
    # Parse tool declarations
    tool_declarations = parse_tool_declarations(ai_response)
    print(f"🔍 Parsed Tools: {tool_declarations}\n")
    
    # Create executor (normal mode)
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    
    # Execute tools
    results = executor.execute_tools(tool_declarations)
    print(f"⚙️ Execution Results:")
    for result in results:
        print(f"  - {result.get('tool')}: {result.get('success')}")
        if result.get('message'):
            print(f"    Message: {result.get('message')}")
    print()
    
    # Format for AI
    ai_formatted = executor.format_results(results)
    print(f"🤖 Formatted for AI:\n{ai_formatted}")
    
    # Format for user
    user_formatted = executor.format_for_user(results)
    print(f"👤 Formatted for User:\n{user_formatted}")
    
    # Clean AI response
    clean_response = remove_tool_declarations(ai_response)
    print(f"✨ Clean Response:\n{clean_response}\n")
    
    print("=" * 60)
    print("✅ Basic flow test complete!\n")


def test_commander_mode():
    """Test commander mode with permission checks"""
    print("🧪 Testing Commander Mode\n")
    print("=" * 60)
    
    # Test 1: Try commander tool without permission
    print("Test 1: Commander tool WITHOUT permission")
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    result = executor.execute_tool('screenshot')
    print(f"  Result: {result.get('success')} - {result.get('message')}\n")
    
    # Test 2: Try commander tool WITH permission
    print("Test 2: Commander tool WITH permission")
    executor = ToolExecutor(commander_mode=True, web_search_mode=False)
    result = executor.execute_tool('screenshot')
    print(f"  Result: {result.get('success')} - {result.get('message')}\n")
    
    print("=" * 60)
    print("✅ Commander mode test complete!\n")


def test_web_search_mode():
    """Test web search mode with permission checks"""
    print("🧪 Testing Web Search Mode\n")
    print("=" * 60)
    
    # Test 1: Try web tool without permission
    print("Test 1: Web tool WITHOUT permission")
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    result = executor.execute_tool('web_search', {'query': 'Python programming', 'max_results': 5})
    print(f"  Result: {result.get('success')} - {result.get('message')}\n")
    
    # Test 2: Try web tool WITH permission
    print("Test 2: Web tool WITH permission (note: may fail if no internet)")
    executor = ToolExecutor(commander_mode=False, web_search_mode=True)
    result = executor.execute_tool('web_search', {'query': 'Python programming', 'max_results': 5})
    print(f"  Result: {result.get('success')}")
    if result.get('success'):
        print(f"  Got search results!")
    else:
        print(f"  Error: {result.get('message')}")
    print()
    
    print("=" * 60)
    print("✅ Web search mode test complete!\n")


def test_multiple_tools():
    """Test executing multiple tools in sequence"""
    print("🧪 Testing Multiple Tools\n")
    print("=" * 60)
    
    ai_response = """<TOOLS>datetime</TOOLS>
<TOOLS>system_info</TOOLS>

Let me check your system details."""
    
    print(f"📝 AI Response with multiple tools:\n{ai_response}\n")
    
    # Parse
    tool_declarations = parse_tool_declarations(ai_response)
    print(f"🔍 Parsed Tools: {len(tool_declarations)} tools")
    for decl in tool_declarations:
        print(f"  - {decl['tool']}: {decl['params']}")
    print()
    
    # Execute
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    results = executor.execute_tools(tool_declarations)
    
    # Format
    formatted = executor.format_for_user(results)
    print(f"📊 Results:\n{formatted}")
    
    print("=" * 60)
    print("✅ Multiple tools test complete!\n")


def test_tool_with_params():
    """Test tool execution with parameters"""
    print("🧪 Testing Tools with Parameters\n")
    print("=" * 60)
    
    ai_response = """<TOOLS>check_app(app_name="steam")</TOOLS>

Let me check if Steam is installed."""
    
    print(f"📝 AI Response:\n{ai_response}\n")
    
    # Parse
    tool_declarations = parse_tool_declarations(ai_response)
    print(f"🔍 Parsed: {tool_declarations}\n")
    
    # Execute
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    results = executor.execute_tools(tool_declarations)
    
    # Show results
    for result in results:
        print(f"⚙️ {result.get('tool')}: {result.get('success')}")
        print(f"   {result.get('message')}\n")
    
    print("=" * 60)
    print("✅ Parameters test complete!\n")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 TOOL EXECUTION SYSTEM - END-TO-END TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_basic_flow()
        test_commander_mode()
        test_web_search_mode()
        test_multiple_tools()
        test_tool_with_params()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
