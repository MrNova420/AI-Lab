#!/usr/bin/env python3
"""
AI-Integrated Commander Chat
Allows AI to use Commander tools via function calling
"""

import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.commander import Commander

# Tool definitions for AI
COMMANDER_TOOLS = {
    "mouse_move": {
        "description": "Move the mouse cursor to a specific position on screen",
        "parameters": {
            "x": "x coordinate or 'left'/'center'/'right'",
            "y": "y coordinate or 'top'/'center'/'bottom'"
        },
        "example": "To move mouse to top right: mouse_move(x='right', y='top')"
    },
    "mouse_click": {
        "description": "Click the mouse button",
        "parameters": {
            "button": "'left', 'right', or 'middle'",
            "clicks": "number of clicks (1 or 2)"
        },
        "example": "To left click: mouse_click(button='left', clicks=1)"
    },
    "keyboard_type": {
        "description": "Type text on the keyboard",
        "parameters": {
            "text": "the text to type"
        },
        "example": "To type hello: keyboard_type(text='hello world')"
    },
    "keyboard_press": {
        "description": "Press a specific key",
        "parameters": {
            "key": "key name like 'enter', 'escape', 'tab', 'space'"
        },
        "example": "To press enter: keyboard_press(key='enter')"
    },
    "open_app": {
        "description": "Open a Windows application. Use actual .exe names or common app names",
        "parameters": {
            "app": "Application name like 'chrome', 'notepad', 'steam', 'discord', 'spotify', 'code' (VS Code)"
        },
        "example": "To open Steam desktop app: open_app(app='steam')"
    },
    "open_url": {
        "description": "Open a URL in the default web browser",
        "parameters": {
            "url": "full URL to open"
        },
        "example": "To open Steam website: open_url(url='https://store.steampowered.com')"
    },
    "screenshot": {
        "description": "Take a screenshot of the screen and save it to Downloads",
        "parameters": {},
        "example": "To take screenshot: screenshot()"
    },
    "clipboard_copy": {
        "description": "Copy text to the Windows clipboard",
        "parameters": {
            "text": "text to copy"
        },
        "example": "To copy text: clipboard_copy(text='hello')"
    }
}

def get_system_prompt_with_tools():
    """Generate system prompt with available Commander tools"""
    
    tools_description = "You have access to the following system control tools:\n\n"
    
    for tool_name, tool_info in COMMANDER_TOOLS.items():
        tools_description += f"**{tool_name}**: {tool_info['description']}\n"
        tools_description += f"  Parameters: {tool_info['parameters']}\n"
        tools_description += f"  Example: {tool_info['example']}\n\n"
    
    system_prompt = f"""You are NovaForge, an AI assistant with the ability to control the user's computer.

{tools_description}

IMPORTANT INSTRUCTIONS FOR TOOL USE:

1. When the user asks you to do something that requires system control, YOU MUST USE THE TOOLS.

2. To use a tool, output EXACTLY in this format on its own line:
   TOOL_CALL: tool_name(param1=value1, param2=value2)

3. Examples:
   - User: "open steam app" → You output: TOOL_CALL: open_app(app='steam')
   - User: "open steam website" → You output: TOOL_CALL: open_url(url='https://store.steampowered.com')
   - User: "take a screenshot" → You output: TOOL_CALL: screenshot()
   - User: "type hello" → You output: TOOL_CALL: keyboard_type(text='hello')

4. IMPORTANT DISTINCTIONS:
   - "open steam" or "open steam app" = Use open_app(app='steam') for desktop application
   - "open steam website" or "go to steam site" = Use open_url(url='https://store.steampowered.com')
   - Always prefer desktop apps when user says "open [app name]" without specifying website

5. After outputting TOOL_CALL, also provide a friendly response to the user.

6. You can call multiple tools by outputting multiple TOOL_CALL lines.

7. If user asks for something you cannot do, explain politely.

Example full response:
User: "open steam and take a screenshot"
You: "TOOL_CALL: open_app(app='steam')
TOOL_CALL: screenshot()
I've opened Steam and taken a screenshot for you!"

Remember: Be conversational and helpful. Use tools when appropriate."""

    return system_prompt

def parse_tool_calls(ai_response):
    """Extract tool calls from AI response"""
    tool_calls = []
    lines = ai_response.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('TOOL_CALL:'):
            # Extract tool call
            tool_call_str = line.replace('TOOL_CALL:', '').strip()
            
            # Parse tool name and parameters
            if '(' in tool_call_str:
                tool_name = tool_call_str.split('(')[0].strip()
                params_str = tool_call_str.split('(')[1].rstrip(')')
                
                # Parse parameters
                params = {}
                if params_str:
                    for param in params_str.split(','):
                        if '=' in param:
                            key, value = param.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            params[key] = value
                
                tool_calls.append({
                    'tool': tool_name,
                    'params': params
                })
    
    return tool_calls

def execute_tool_calls(tool_calls, commander):
    """
    Execute tool calls dynamically using the tools registry
    This replaces the hardcoded if/elif chain with dynamic imports
    """
    import sys
    import os
    import importlib
    
    # Add tools directory to path
    tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tools')
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
    
    from tools import TOOLS
    
    results = []
    
    for call in tool_calls:
        tool_name = call['tool']
        params = call.get('params', {})
        
        try:
            # Special handling for Commander methods (backward compatibility)
            if tool_name in ['mouse_move', 'mouse_click', 'keyboard_type', 'keyboard_press', 
                            'open_app', 'open_url', 'screenshot', 'clipboard_copy']:
                if tool_name == 'mouse_move':
                    result = commander.mouse_move(params.get('x'), params.get('y'))
                elif tool_name == 'mouse_click':
                    result = commander.mouse_click(params.get('button', 'left'), int(params.get('clicks', 1)))
                elif tool_name == 'keyboard_type':
                    result = commander.keyboard_type(params.get('text'))
                elif tool_name == 'keyboard_press':
                    result = commander.keyboard_press(params.get('key'))
                elif tool_name == 'open_app':
                    result = commander.open_app(params.get('app'))
                elif tool_name == 'open_url':
                    result = commander.open_url(params.get('url'))
                elif tool_name == 'screenshot':
                    result = commander.screenshot()
                elif tool_name == 'clipboard_copy':
                    result = commander.clipboard_copy(params.get('text'))
            else:
                # Dynamic tool loading from registry
                tool_found = False
                for category, tools in TOOLS.items():
                    if tool_name in tools:
                        tool_info = tools[tool_name]
                        module_name = tool_info['module']
                        function_name = tool_info['function']
                        
                        # Import module and get function
                        module = importlib.import_module(module_name)
                        func = getattr(module, function_name)
                        
                        # Call function with params
                        result = func(**params)
                        tool_found = True
                        break
                
                if not tool_found:
                    result = {'success': False, 'error': f'Unknown tool: {tool_name}'}
            
            results.append({
                'tool': tool_name,
                'params': params,
                'result': result
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            results.append({
                'tool': tool_name,
                'params': params,
                'result': {'success': False, 'error': str(e)}
            })
    
    return results

def remove_tool_calls_from_response(ai_response):
    """Remove TOOL_CALL lines from AI response to get clean message"""
    lines = ai_response.split('\n')
    clean_lines = [line for line in lines if not line.strip().startswith('TOOL_CALL:')]
    return '\n'.join(clean_lines).strip()

def main():
    """Test function calling"""
    if len(sys.argv) < 2:
        print("Usage: ai_commander_chat.py <user_message>")
        sys.exit(1)
    
    user_message = " ".join(sys.argv[1:])
    
    # Initialize commander
    commander = Commander()
    
    # Get system prompt with tools
    system_prompt = get_system_prompt_with_tools()
    
    # For testing, simulate AI response
    # In real implementation, this calls Ollama
    print("System Prompt Preview:")
    print(system_prompt[:500] + "...")
    print("\n---\n")
    print(f"User: {user_message}")
    print("\nNOTE: In production, this would call Ollama with the system prompt and user message.")
    print("The AI would then decide whether to use tools based on the request.")

if __name__ == "__main__":
    main()
