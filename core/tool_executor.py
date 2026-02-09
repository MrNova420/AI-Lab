#!/usr/bin/env python3
"""
Tool Execution Engine
Executes tools declared by the AI in a safe, dynamic way
"""

import importlib
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools import TOOLS


class ToolExecutor:
    """Execute tools dynamically from the registry"""
    
    def __init__(self, commander_mode=False, web_search_mode=False):
        self.commander_mode = commander_mode
        self.web_search_mode = web_search_mode
        self.tool_cache = {}  # Cache imported modules
    
    def execute_tool(self, tool_name, params=None):
        """
        Execute a single tool by name
        
        Args:
            tool_name: Name of the tool (e.g., 'datetime', 'open_app')
            params: Dict of parameters (optional)
            
        Returns:
            Dict with 'success', 'message', 'data' keys
        """
        if params is None:
            params = {}
        
        # Find tool in registry
        tool_info = self._find_tool(tool_name)
        
        if not tool_info:
            return {
                'success': False,
                'tool': tool_name,
                'message': f"Tool '{tool_name}' not found",
                'error': 'TOOL_NOT_FOUND'
            }
        
        # Check permissions
        requires_commander = tool_info.get('requires_commander', False)
        requires_web = tool_info.get('requires_web', False)
        
        if requires_commander and not self.commander_mode:
            return {
                'success': False,
                'tool': tool_name,
                'message': f"Tool '{tool_name}' requires Commander Mode",
                'error': 'PERMISSION_DENIED'
            }
        
        if requires_web and not self.web_search_mode:
            return {
                'success': False,
                'tool': tool_name,
                'message': f"Tool '{tool_name}' requires Web Search Mode",
                'error': 'PERMISSION_DENIED'
            }
        
        # Execute tool
        try:
            module_path = tool_info['module']
            function_name = tool_info['function']
            
            # Import module (cached)
            if module_path not in self.tool_cache:
                module = importlib.import_module(module_path)
                self.tool_cache[module_path] = module
            else:
                module = self.tool_cache[module_path]
            
            # Get function
            function = getattr(module, function_name)
            
            # Call function with params
            if params:
                result = function(**params)
            else:
                result = function()
            
            # Ensure result is a dict
            if not isinstance(result, dict):
                result = {'success': True, 'data': result}
            
            result['tool'] = tool_name
            return result
            
        except Exception as e:
            return {
                'success': False,
                'tool': tool_name,
                'message': f"Tool execution failed: {str(e)}",
                'error': 'EXECUTION_ERROR',
                'exception': str(e)
            }
    
    def execute_tools(self, tool_declarations):
        """
        Execute multiple tools
        
        Args:
            tool_declarations: List of dicts with 'tool' and 'params' keys
            
        Returns:
            List of results
        """
        results = []
        for declaration in tool_declarations:
            tool_name = declaration.get('tool')
            params = declaration.get('params', {})
            result = self.execute_tool(tool_name, params)
            results.append(result)
        return results
    
    def _find_tool(self, tool_name):
        """Find tool in registry by name"""
        for category, tools in TOOLS.items():
            if tool_name in tools:
                return tools[tool_name]
        return None
    
    def format_results(self, results):
        """
        Format tool results for AI to read
        
        Args:
            results: List of tool execution results
            
        Returns:
            Formatted string
        """
        if not results:
            return ""
        
        formatted = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        formatted += "🛠️ TOOL RESULTS:\n"
        formatted += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for result in results:
            tool_name = result.get('tool', 'unknown')
            success = result.get('success', False)
            
            if success:
                formatted += f"✅ {tool_name}:\n"
                
                # Format message or data
                if 'message' in result:
                    formatted += f"   {result['message']}\n"
                elif 'data' in result:
                    data = result['data']
                    if isinstance(data, dict):
                        for key, value in data.items():
                            formatted += f"   {key}: {value}\n"
                    else:
                        formatted += f"   {data}\n"
                
            else:
                formatted += f"❌ {tool_name} FAILED:\n"
                formatted += f"   {result.get('message', 'Unknown error')}\n"
            
            formatted += "\n"
        
        formatted += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        return formatted
    
    def format_for_user(self, results):
        """
        Format tool results for user display (shorter, cleaner)
        
        Args:
            results: List of tool execution results
            
        Returns:
            Formatted string
        """
        if not results:
            return ""
        
        formatted = ""
        
        for result in results:
            tool_name = result.get('tool', 'unknown')
            success = result.get('success', False)
            
            if success:
                formatted += f"🛠️ {tool_name}: "
                
                # Get message
                message = result.get('message', '')
                if message:
                    formatted += f"{message}\n"
                else:
                    formatted += "✓\n"
            else:
                formatted += f"⚠️ {tool_name}: {result.get('message', 'Failed')}\n"
        
        return formatted


def test_executor():
    """Test the tool executor"""
    print("🧪 Testing Tool Executor\n")
    
    # Test normal mode
    executor = ToolExecutor(commander_mode=False, web_search_mode=False)
    
    print("1. Test datetime tool (should work):")
    result = executor.execute_tool('datetime')
    print(f"   Result: {result}\n")
    
    print("2. Test system_info tool (should work):")
    result = executor.execute_tool('system_info')
    print(f"   Result: {result}\n")
    
    print("3. Test open_app without commander mode (should fail):")
    result = executor.execute_tool('open_app', {'app': 'steam'})
    print(f"   Result: {result}\n")
    
    # Test commander mode
    executor = ToolExecutor(commander_mode=True, web_search_mode=False)
    
    print("4. Test open_app WITH commander mode (should work):")
    result = executor.execute_tool('open_app', {'app': 'steam'})
    print(f"   Result: {result}\n")
    
    print("5. Test multiple tools:")
    results = executor.execute_tools([
        {'tool': 'datetime', 'params': {}},
        {'tool': 'system_info', 'params': {}}
    ])
    print("   Results:")
    for r in results:
        print(f"   - {r['tool']}: {r.get('message', r.get('success'))}")


if __name__ == '__main__':
    test_executor()
