#!/usr/bin/env python3
"""
Smart AI Response Parser
Extracts tool calls from AI's intelligent response
No hardcoded keywords - AI decides what tools to use
"""

import re
import json

def parse_tool_declarations(ai_response):
    """
    Parse <TOOLS>...</TOOLS> declarations from AI response
    
    Examples:
    <TOOLS>current_date</TOOLS>
    <TOOLS>open_app(app="steam")</TOOLS>
    <TOOLS>mouse_move(x=100, y=200)</TOOLS>
    """
    tools = []
    
    # Find all <TOOLS>...</TOOLS> blocks
    tool_pattern = r'<TOOLS>(.*?)</TOOLS>'
    matches = re.findall(tool_pattern, ai_response, re.IGNORECASE)
    
    for match in matches:
        tool_call = match.strip()
        
        # Parse function call format: tool_name(param1=value1, param2=value2)
        func_match = re.match(r'(\w+)\((.*?)\)', tool_call)
        
        if func_match:
            tool_name = func_match.group(1)
            params_str = func_match.group(2)
            
            # Parse parameters
            params = {}
            if params_str.strip():
                # Split by comma but respect quotes
                param_parts = re.findall(r'(\w+)=([^,]+)', params_str)
                for param_name, param_value in param_parts:
                    param_value = param_value.strip()
                    # Remove quotes
                    if param_value.startswith('"') and param_value.endswith('"'):
                        param_value = param_value[1:-1]
                    elif param_value.startswith("'") and param_value.endswith("'"):
                        param_value = param_value[1:-1]
                    # Try to convert to number
                    try:
                        if '.' in param_value:
                            param_value = float(param_value)
                        else:
                            param_value = int(param_value)
                    except ValueError:
                        pass  # Keep as string
                    
                    params[param_name] = param_value
            
            tools.append({
                'tool': tool_name,
                'params': params
            })
        else:
            # Simple tool name without parameters
            tools.append({
                'tool': tool_call,
                'params': {}
            })
    
    return tools


def remove_tool_declarations(ai_response):
    """Remove <TOOLS>...</TOOLS> from response to get clean message"""
    cleaned = re.sub(r'<TOOLS>.*?</TOOLS>\s*', '', ai_response, flags=re.IGNORECASE)
    return cleaned.strip()


def test_parser():
    """Test the parser"""
    test_cases = [
        '<TOOLS>current_date</TOOLS>\n\nLet me check the date.',
        '<TOOLS>open_app(app="steam")</TOOLS>\n\nOpening Steam!',
        '<TOOLS>mouse_move(x=100, y=200)</TOOLS>\n\nMoving mouse.',
        'Just a normal response with no tools.',
        '<TOOLS>screenshot</TOOLS>\n<TOOLS>open_app(app="notepad")</TOOLS>\n\nDone!',
    ]
    
    for test in test_cases:
        print(f"\nInput: {test[:50]}...")
        tools = parse_tool_declarations(test)
        clean = remove_tool_declarations(test)
        print(f"Tools: {tools}")
        print(f"Clean: {clean}")


if __name__ == '__main__':
    test_parser()
