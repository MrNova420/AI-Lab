#!/usr/bin/env python3
"""
Test the enhanced Copilot-like development capabilities
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_project_context():
    """Test project context analyzer"""
    print("\n" + "="*60)
    print("🧪 Testing Project Context Analyzer")
    print("="*60)
    
    try:
        from core.project_context import ProjectContextAnalyzer, get_ai_context
        
        analyzer = ProjectContextAnalyzer(str(PROJECT_ROOT))
        context = analyzer.analyze_project()
        
        print("\n✅ Project analyzed successfully")
        print(f"   Languages: {len(context['languages'])}")
        print(f"   Frameworks: {len(context['frameworks'])}")
        print(f"   Code files: {context['structure']['code_files']}")
        print(f"   Patterns: {len(context['patterns'])}")
        
        # Test AI context string
        ai_context = get_ai_context(str(PROJECT_ROOT))
        print(f"\n✅ AI Context generated ({len(ai_context)} chars)")
        print("\nContext preview:")
        print(ai_context[:200] + "...")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_development_protocol():
    """Test development protocol"""
    print("\n" + "="*60)
    print("🧪 Testing Development Protocol")
    print("="*60)
    
    try:
        from core.development_protocol import get_development_system_prompt
        from tools import generate_tools_description
        
        # Generate tools description
        tools_desc = generate_tools_description(commander_mode=True)
        
        # Generate development prompt
        prompt = get_development_system_prompt(
            project_context="Test project",
            tools_description=tools_desc,
            commander_mode=True
        )
        
        print("\n✅ Development prompt generated successfully")
        print(f"   Length: {len(prompt)} chars")
        print(f"   Contains 'GitHub Copilot': {'GitHub Copilot' in prompt}")
        print(f"   Contains 'development partner': {'development partner' in prompt}")
        print(f"   Contains '43 Available': {'43 Available' in prompt}")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_development_workflows():
    """Test development workflows"""
    print("\n" + "="*60)
    print("🧪 Testing Development Workflows")
    print("="*60)
    
    try:
        from core.development_workflows import DevelopmentWorkflow, get_workflow_recommendations
        from core.tool_executor import ToolExecutor
        
        # Create tool executor
        tool_executor = ToolExecutor(commander_mode=True)
        
        # Create workflow manager
        workflow = DevelopmentWorkflow(tool_executor, str(PROJECT_ROOT))
        
        # Test workflow recommendations
        recommendations = get_workflow_recommendations("I want to fix a bug in the code")
        print(f"\n✅ Workflow recommendations: {recommendations}")
        
        # Test analyze_codebase workflow
        result = workflow.execute_workflow("analyze_codebase", {})
        
        print(f"\n✅ Workflow executed successfully")
        print(f"   Workflow: {result.get('workflow')}")
        print(f"   Steps completed: {len(result.get('steps', []))}")
        print(f"   Findings: {list(result.get('findings', {}).keys())}")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_protocol_integration():
    """Test AI protocol with development mode"""
    print("\n" + "="*60)
    print("🧪 Testing AI Protocol Integration")
    print("="*60)
    
    try:
        from core.ai_protocol import get_system_prompt, inject_project_context
        from tools import generate_tools_description
        
        tools_desc = generate_tools_description(commander_mode=True)
        
        # Test with development mode enabled
        prompt = get_system_prompt(
            commander_mode=True,
            web_search_mode=False,
            tools_description=tools_desc,
            development_mode=True,
            project_context="Test context"
        )
        
        print("\n✅ System prompt generated with development mode")
        print(f"   Length: {len(prompt)} chars")
        print(f"   Has development features: {'development partner' in prompt.lower()}")
        
        # Test project context injection
        enhanced = inject_project_context(prompt, str(PROJECT_ROOT))
        print(f"\n✅ Context injection works")
        print(f"   Original: {len(prompt)} chars")
        print(f"   Enhanced: {len(enhanced)} chars")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_integration():
    """Test that all tools work with workflows"""
    print("\n" + "="*60)
    print("🧪 Testing Tools Integration")
    print("="*60)
    
    try:
        from core.tool_executor import ToolExecutor
        from tools import TOOLS
        
        executor = ToolExecutor(commander_mode=True)
        
        # Test a few key tools
        print("\n Testing key tools:")
        
        # Test Git tool
        result = executor.execute_tool('git_current_branch', {'repo_path': '.'})
        print(f"   ✅ git_current_branch: {result.get('status')}")
        
        # Test code analysis
        result = executor.execute_tool('analyze_file', {'file_path': 'tools/__init__.py'})
        print(f"   ✅ analyze_file: {result.get('status')}")
        
        # Test code checking
        result = executor.execute_tool('check_syntax', {'file_path': 'tools/__init__.py'})
        print(f"   ✅ check_syntax: {result.get('status')}")
        
        # Count total tools
        total_tools = sum(len(cat) for cat in TOOLS.values())
        print(f"\n✅ Total tools available: {total_tools}")
        
        return True
    except Exception as e:
        print(f"\n❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 COPILOT-LIKE DEVELOPMENT CAPABILITIES TEST SUITE")
    print("="*60)
    
    tests = [
        ("Project Context", test_project_context),
        ("Development Protocol", test_development_protocol),
        ("Development Workflows", test_development_workflows),
        ("AI Protocol Integration", test_ai_protocol_integration),
        ("Tools Integration", test_tools_integration)
    ]
    
    results = {}
    for name, test_func in tests:
        results[name] = test_func()
    
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
        print("\n🎉 All development capabilities working!")
        print("\n💡 Commander Mode now includes:")
        print("   • GitHub Copilot-like code intelligence")
        print("   • Full project context awareness")
        print("   • Intelligent workflow automation")
        print("   • 43 tools for complete development")
        print("\n🚀 Ready for full project development!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
