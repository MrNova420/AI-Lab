#!/usr/bin/env python3
"""
Chat streaming script for desktop app.
Sends messages to Ollama and streams tokens back as JSON.
Supports Commander mode with AI tool calling.
"""
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.project_manager import ProjectManager
from core.runtime.manager import ModelRuntimeManager
from scripts.ai_commander_chat import get_system_prompt_with_tools, parse_tool_calls, execute_tool_calls, remove_tool_calls_from_response
from scripts.commander import Commander

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"type": "error", "message": "No message provided"}))
        sys.exit(1)
    
    user_message = sys.argv[1]
    history = json.loads(sys.argv[2]) if len(sys.argv) > 2 else []
    commander_mode = sys.argv[3].lower() == 'true' if len(sys.argv) > 3 else False
    
    try:
        # Initialize managers
        pm = ProjectManager(str(PROJECT_ROOT))
        project_config = pm.get_active_project_config()
        
        runtime_mgr = ModelRuntimeManager(str(PROJECT_ROOT))
        driver = runtime_mgr.get_driver(project_config)
        
        # If commander mode, use special system prompt with tools
        if commander_mode:
            system_prompt = get_system_prompt_with_tools()
            
            # Inject system prompt at the beginning if not already present
            if not history or history[0].get('role') != 'system':
                history.insert(0, {"role": "system", "content": system_prompt})
            else:
                history[0]['content'] = system_prompt
        
        # Add user message to history
        history.append({"role": "user", "content": user_message})
        
        # Stream response
        full_response = ""
        for token in driver.generate(history, stream=True):
            full_response += token
            print(json.dumps({"type": "token", "token": token}), flush=True)
        
        # If commander mode, check for tool calls
        if commander_mode:
            tool_calls = parse_tool_calls(full_response)
            
            if tool_calls:
                # Execute tools
                commander = Commander()
                results = execute_tool_calls(tool_calls, commander)
                
                # Send tool execution results
                print(json.dumps({"type": "tool_results", "results": results}), flush=True)
                
                # Get clean response without TOOL_CALL lines
                clean_response = remove_tool_calls_from_response(full_response)
                print(json.dumps({"type": "done", "full_response": clean_response, "tool_calls": tool_calls, "tool_results": results}), flush=True)
            else:
                print(json.dumps({"type": "done", "full_response": full_response}), flush=True)
        else:
            print(json.dumps({"type": "done", "full_response": full_response}), flush=True)
        
    except Exception as e:
        print(json.dumps({"type": "error", "message": str(e)}), flush=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
