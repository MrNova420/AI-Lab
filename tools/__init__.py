"""
NovaForge AI Tools Registry
All AI capabilities are registered here - AI analyzes and decides when to use them
"""

# Tool categories
TOOLS = {
    "system": {
        "current_date": {
            "module": "tools.system.info",
            "function": "get_current_date",
            "description": "Get the current date",
            "params": {},
            "requires_commander": False
        },
        "current_time": {
            "module": "tools.system.info",
            "function": "get_current_time",
            "description": "Get the current time",
            "params": {},
            "requires_commander": False
        },
        "current_datetime": {
            "module": "tools.system.info",
            "function": "get_current_datetime",
            "description": "Get the current date and time",
            "params": {},
            "requires_commander": False
        },
        "system_info": {
            "module": "tools.system.info",
            "function": "get_system_info",
            "description": "Get system information (OS, version, architecture)",
            "params": {},
            "requires_commander": False
        },
        "user_info": {
            "module": "tools.system.info",
            "function": "get_user_info",
            "description": "Get current user information",
            "params": {},
            "requires_commander": False
        },
        "screenshot": {
            "module": "tools.system.screenshot",
            "function": "take_screenshot",
            "description": "Capture a screenshot of the screen",
            "params": {},
            "requires_commander": True
        },
        "open_app": {
            "module": "tools.system.apps",
            "function": "open_application",
            "description": "Open a desktop application",
            "params": {"app": "string"},
            "requires_commander": True
        },
        "close_app": {
            "module": "tools.system.apps",
            "function": "close_application",
            "description": "Close a running application",
            "params": {"app": "string"},
            "requires_commander": True
        },
        "analyze_system": {
            "module": "tools.system.analyzer",
            "function": "analyze_system",
            "description": "Get comprehensive system information (OS, version, architecture, etc.)",
            "params": {},
            "requires_commander": False
        },
        "check_running": {
            "module": "tools.system.analyzer",
            "function": "check_what_is_running",
            "description": "See what processes are currently running on the system",
            "params": {},
            "requires_commander": False
        },
        "check_app": {
            "module": "tools.system.analyzer",
            "function": "check_if_app_exists",
            "description": "Check if a specific application is installed",
            "params": {"app_name": "string"},
            "requires_commander": False
        },
        "list_apps": {
            "module": "tools.system.analyzer",
            "function": "get_available_apps",
            "description": "Get list of commonly installed applications",
            "params": {},
            "requires_commander": False
        },
        "analyze_result": {
            "module": "tools.system.analyzer",
            "function": "analyze_result",
            "description": "Analyze the result of a previous command (success/failure, error classification, suggestions)",
            "params": {"command": "string", "result": "dict"},
            "requires_commander": False
        }
    },
    "web": {
        "open_url": {
            "module": "tools.web.browser",
            "function": "open_url",
            "description": "Open a URL in the browser",
            "params": {"url": "string"},
            "requires_commander": False
        },
        "web_search": {
            "module": "tools.web.search",
            "function": "web_search",
            "description": "Search the web using multiple sources (DuckDuckGo, etc). Returns summarized results with titles, URLs, and snippets. Use quick=True for fast results.",
            "params": {"query": "string", "quick": "bool"},
            "requires_commander": False,
            "requires_web": True
        },
        "verify_info": {
            "module": "tools.web.search",
            "function": "verify_information",
            "description": "Verify a claim by searching multiple sources and checking consistency. Best for fact-checking.",
            "params": {"query": "string", "claim": "string"},
            "requires_commander": False,
            "requires_web": True
        },
        "deep_search": {
            "module": "tools.web.search",
            "function": "search_multiple_sources",
            "description": "Deep search across multiple sources with aggregation and verification. Best for research and comprehensive information gathering.",
            "params": {"query": "string"},
            "requires_commander": False,
            "requires_web": True
        }
    },
    "input": {
        "mouse_move": {
            "module": "tools.input.mouse",
            "function": "move_mouse",
            "description": "Move the mouse cursor to coordinates",
            "params": {"x": "int", "y": "int"},
            "requires_commander": True
        },
        "mouse_click": {
            "module": "tools.input.mouse",
            "function": "click_mouse",
            "description": "Click the mouse button",
            "params": {"button": "string", "double": "bool"},
            "requires_commander": True
        },
        "keyboard_type": {
            "module": "tools.input.keyboard",
            "function": "type_text",
            "description": "Type text using keyboard",
            "params": {"text": "string"},
            "requires_commander": True
        },
        "keyboard_press": {
            "module": "tools.input.keyboard",
            "function": "press_key",
            "description": "Press a special key",
            "params": {"key": "string"},
            "requires_commander": True
        }
    }
}

def get_available_tools(commander_mode=False, web_search_mode=False):
    """
    Get list of available tools based on modes
    commander_mode = all system control tools
    web_search_mode = web search tools
    normal = only safe info-gathering tools
    """
    available = {}
    
    for category, tools in TOOLS.items():
        available[category] = {}
        for tool_name, tool_info in tools.items():
            # Include tool if:
            # 1. Commander mode is enabled AND tool requires commander, OR
            # 2. Web search mode is enabled AND tool requires web, OR
            # 3. Tool doesn't require either mode
            
            requires_commander = tool_info.get("requires_commander", False)
            requires_web = tool_info.get("requires_web", False)
            
            if requires_commander and not commander_mode:
                continue  # Skip commander tools if not enabled
            
            if requires_web and not web_search_mode:
                continue  # Skip web tools if not enabled
            
            available[category][tool_name] = tool_info
    
    return available


def generate_tools_description(commander_mode=False, web_search_mode=False):
    """
    Generate natural language description of available tools
    This goes into the system prompt
    """
    tools = get_available_tools(commander_mode, web_search_mode)
    
    if not any(tools.values()):
        return "You currently have no tools available. You can only chat."
    
    desc = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    desc += "🛠️ AVAILABLE TOOLS:\n"
    desc += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for category, category_tools in tools.items():
        if not category_tools:
            continue
            
        desc += f"**{category.upper()} TOOLS:**\n"
        for tool_name, tool_info in category_tools.items():
            params_str = ", ".join([f"{k}: {v}" for k, v in tool_info["params"].items()])
            if params_str:
                desc += f"  • {tool_name}({params_str}) - {tool_info['description']}\n"
            else:
                desc += f"  • {tool_name}() - {tool_info['description']}\n"
        desc += "\n"
    
    desc += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # Add intelligence notes
    if commander_mode or web_search_mode:
        desc += "\n💡 **HOW TO USE:**\n"
        
        if web_search_mode:
            desc += "**WEB SEARCH:**\n"
            desc += "  - User asks about current events? Use web_search(query, quick=True)\n"
            desc += "  - Need to verify facts? Use verify_info(query, claim)\n"
            desc += "  - Deep research needed? Use deep_search(query)\n\n"
        
        if commander_mode:
            desc += "**SYSTEM CONTROL:**\n"
            desc += "  - Check if app exists BEFORE opening: check_app(name)\n"
            desc += "  - See what's running: check_running()\n"
            desc += "  - After actions: analyze_result(cmd, result)\n\n"
        
        desc += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    return desc
