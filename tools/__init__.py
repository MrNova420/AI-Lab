"""
NovaForge AI Tools Registry
All AI capabilities are registered here - AI analyzes and decides when to use them
"""

# Tool categories
TOOLS = {
    "system": {
        "datetime": {
            "module": "tools.system.info",
            "function": "get_current_datetime",
            "description": "Get current date AND time together (use this for date/time questions)",
            "params": {},
            "requires_commander": False,
            "requires_verification": False  # Simple tool - just append result
        },
        "system_info": {
            "module": "tools.system.info",
            "function": "get_system_info",
            "description": "Get REAL system information (OS, CPU, RAM, kernel)",
            "params": {},
            "requires_commander": False,
            "requires_verification": True  # Complex - AI should see and verify
        },
        "user_info": {
            "module": "tools.system.info",
            "function": "get_user_info",
            "description": "Get current user information",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        },
        "screenshot": {
            "module": "tools.system.screenshot",
            "function": "take_screenshot",
            "description": "Capture a screenshot of the screen",
            "params": {},
            "requires_commander": True,
            "requires_verification": False
        },
        "open_app": {
            "module": "tools.system.apps",
            "function": "open_application",
            "description": "Open a desktop application",
            "params": {"app": "string"},
            "requires_commander": True,
            "requires_verification": False
        },
        "close_app": {
            "module": "tools.system.apps",
            "function": "close_application",
            "description": "Close a running application",
            "params": {"app": "string"},
            "requires_commander": True,
            "requires_verification": False
        },
        "analyze_system": {
            "module": "tools.system.analyzer",
            "function": "analyze_system",
            "description": "Get comprehensive system information (OS, version, architecture, etc.)",
            "params": {},
            "requires_commander": False,
            "requires_verification": True  # Complex analysis
        },
        "check_running": {
            "module": "tools.system.analyzer",
            "function": "check_what_is_running",
            "description": "See what processes are currently running on the system",
            "params": {},
            "requires_commander": False,
            "requires_verification": True  # Complex data
        },
        "check_app": {
            "module": "tools.system.analyzer",
            "function": "check_if_app_exists",
            "description": "Check if a specific application is installed",
            "params": {"app_name": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "list_apps": {
            "module": "tools.system.analyzer",
            "function": "get_available_apps",
            "description": "Get list of commonly installed applications",
            "params": {},
            "requires_commander": False,
            "requires_verification": True  # Complex list
        },
        "analyze_result": {
            "module": "tools.system.analyzer",
            "function": "analyze_result",
            "description": "Analyze the result of a previous command (success/failure, error classification, suggestions)",
            "params": {"command": "string", "result": "dict"},
            "requires_commander": False,
            "requires_verification": True  # Needs analysis
        }
    },
    "web": {
        "open_url": {
            "module": "tools.web.browser",
            "function": "open_url",
            "description": "Open a URL in the browser",
            "params": {"url": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "web_search": {
            "module": "tools.web.advanced_search",
            "function": "advanced_web_search",
            "description": "🌐 ADVANCED WEB SEARCH: Multi-source search with intelligent prioritization. PRIMARY: 🌟 Grokipedia (newest, best knowledge base - better than Wikipedia!), SECONDARY: 📚 Wikipedia (reliable factual), Then: 🔍 Google, 📖 Wikimedia, Bing. Searches all sources in parallel (3-8 sec). Returns ranked results from knowledge bases first, then search engines. Use this for ANY web search - most comprehensive, up-to-date, and reliable!",
            "params": {"query": "string", "max_results": "int"},
            "requires_commander": False,
            "requires_web": True,
            "requires_verification": True  # Web results need verification
        },
        "deep_research": {
            "module": "tools.web.advanced_search",
            "function": "deep_web_research",
            "description": "🔬 DEEP RESEARCH: Comprehensive 5-step research process: (1) Search Grokipedia+Wikipedia+Google+others, (2) Analyze and rank results, (3) Scrape top pages for full content, (4) Verify facts and cross-reference, (5) Generate intelligent summary with quality score. Prioritizes Grokipedia (best knowledge base) first. Best for in-depth research requiring detailed, verified information from multiple high-quality sources.",
            "params": {"query": "string", "max_results": "int", "scrape_top": "int"},
            "requires_commander": False,
            "requires_web": True,
            "requires_verification": True
        },
        "fact_check": {
            "module": "tools.web.advanced_search",
            "function": "quick_fact_check",
            "description": "✓ FACT CHECK: Quick fact verification across Google, Bing, and DuckDuckGo. Returns verification status, number of sources confirming, and supporting evidence. Use for verifying claims or checking accuracy.",
            "params": {"claim": "string"},
            "requires_commander": False,
            "requires_web": True,
            "requires_verification": True
        },
        "scrape_webpage": {
            "module": "tools.web.advanced_search",
            "function": "scrape_webpage",
            "description": "📄 SCRAPE: Extract clean text content from any webpage. Returns title and main content without ads, navigation, or clutter. Perfect for reading full articles or documentation.",
            "params": {"url": "string"},
            "requires_commander": False,
            "requires_web": True,
            "requires_verification": True
        },
        "scrape_multiple": {
            "module": "tools.web.advanced_search",
            "function": "scrape_multiple_pages",
            "description": "📚 BATCH SCRAPE: Scrape multiple webpages in parallel for fast content extraction. Provide list of URLs to extract content from all at once.",
            "params": {"urls": "list"},
            "requires_commander": False,
            "requires_web": True,
            "requires_verification": True
        }
    },
    "input": {
        "mouse_move": {
            "module": "tools.input.mouse",
            "function": "move_mouse",
            "description": "Move the mouse cursor to coordinates",
            "params": {"x": "int", "y": "int"},
            "requires_commander": True,
            "requires_verification": False
        },
        "mouse_click": {
            "module": "tools.input.mouse",
            "function": "click_mouse",
            "description": "Click the mouse button",
            "params": {"button": "string", "double": "bool"},
            "requires_commander": True,
            "requires_verification": False
        },
        "keyboard_type": {
            "module": "tools.input.keyboard",
            "function": "type_text",
            "description": "Type text using keyboard",
            "params": {"text": "string"},
            "requires_commander": True,
            "requires_verification": False
        },
        "keyboard_press": {
            "module": "tools.input.keyboard",
            "function": "press_key",
            "description": "Press a special key",
            "params": {"key": "string"},
            "requires_commander": True,
            "requires_verification": False
        }
    },
    "files": {
        "read_file": {
            "module": "tools.system.files",
            "function": "read_file",
            "description": "📖 READ FILE: Read contents of a text file. Max 10MB. Returns file content, size, and line count.",
            "params": {"path": "string"},
            "requires_commander": True,
            "requires_verification": True
        },
        "write_file": {
            "module": "tools.system.files",
            "function": "write_file",
            "description": "✍️ WRITE FILE: Write or create a file with content. Creates directories if needed.",
            "params": {"path": "string", "content": "string"},
            "requires_commander": True,  # Writing requires permission
            "requires_verification": True
        },
        "list_files": {
            "module": "tools.system.files",
            "function": "list_files",
            "description": "📁 LIST FILES: List all files and directories in a path. Shows names, sizes, and timestamps.",
            "params": {"directory": "string"},
            "requires_commander": True,
            "requires_verification": True
        },
        "file_info": {
            "module": "tools.system.files",
            "function": "file_info",
            "description": "ℹ️ FILE INFO: Get detailed information about a file (size, dates, permissions, line count).",
            "params": {"path": "string"},
            "requires_commander": True,
            "requires_verification": False
        }
    },
    "processes": {
        "list_processes": {
            "module": "tools.system.processes",
            "function": "list_processes",
            "description": "📊 LIST PROCESSES: Show running processes with CPU and memory usage. Returns top 50 processes.",
            "params": {},
            "requires_commander": True,
            "requires_verification": False
        },
        "process_info": {
            "module": "tools.system.processes",
            "function": "process_info",
            "description": "🔍 PROCESS INFO: Get detailed info about a specific process by PID (CPU, memory, threads, etc.).",
            "params": {"pid": "int"},
            "requires_commander": True,
            "requires_verification": False
        },
        "find_process": {
            "module": "tools.system.processes",
            "function": "find_process",
            "description": "🔎 FIND PROCESS: Search for processes by name (case-insensitive). Returns matching PIDs.",
            "params": {"name": "string"},
            "requires_commander": True,
            "requires_verification": False
        }
    },
    "network": {
        "ping": {
            "module": "tools.network.network_tools",
            "function": "ping",
            "description": "🌐 PING: Check network connectivity to a host. Returns latency and success status.",
            "params": {"host": "string", "count": "int"},
            "requires_commander": False,
            "requires_verification": False
        },
        "network_info": {
            "module": "tools.network.network_tools",
            "function": "network_info",
            "description": "📡 NETWORK INFO: Get network interface information (IP address, hostname, FQDN).",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        },
        "traceroute": {
            "module": "tools.network.network_tools",
            "function": "traceroute",
            "description": "🗺️ TRACEROUTE: Trace the network path to a host. Shows all hops.",
            "params": {"host": "string", "max_hops": "int"},
            "requires_commander": False,
            "requires_verification": True
        },
        "dns_lookup": {
            "module": "tools.network.network_tools",
            "function": "dns_lookup",
            "description": "🔍 DNS LOOKUP: Resolve hostname to IP address(es). Shows aliases and canonical name.",
            "params": {"hostname": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "check_port": {
            "module": "tools.network.network_tools",
            "function": "check_port",
            "description": "🔌 CHECK PORT: Check if a port is open on a host. Useful for service availability.",
            "params": {"host": "string", "port": "int", "timeout": "int"},
            "requires_commander": False,
            "requires_verification": False
        }
    },
    "git": {
        "git_status": {
            "module": "tools.git.git_tools",
            "function": "git_status",
            "description": "📊 GIT STATUS: Get repository status (modified, staged, untracked files).",
            "params": {"repo_path": "string"},
            "requires_commander": False,
            "requires_verification": True
        },
        "git_log": {
            "module": "tools.git.git_tools",
            "function": "git_log",
            "description": "📜 GIT LOG: Get recent commit history with messages and authors.",
            "params": {"repo_path": "string", "max_count": "int"},
            "requires_commander": False,
            "requires_verification": True
        },
        "git_diff": {
            "module": "tools.git.git_tools",
            "function": "git_diff",
            "description": "🔍 GIT DIFF: Show changes in repository (unstaged and staged diffs).",
            "params": {"repo_path": "string", "file_path": "string"},
            "requires_commander": False,
            "requires_verification": True
        },
        "git_branch_list": {
            "module": "tools.git.git_tools",
            "function": "git_branch_list",
            "description": "🌳 GIT BRANCHES: List all branches in repository (local and remote).",
            "params": {"repo_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "git_current_branch": {
            "module": "tools.git.git_tools",
            "function": "git_current_branch",
            "description": "🎯 CURRENT BRANCH: Get current branch name and tracking information.",
            "params": {"repo_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        }
    },
    "code": {
        "analyze_file": {
            "module": "tools.code.code_tools",
            "function": "analyze_file",
            "description": "🔬 ANALYZE FILE: Analyze code file structure (lines, functions, classes, complexity).",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": True
        },
        "find_todos": {
            "module": "tools.code.code_tools",
            "function": "find_todos",
            "description": "📝 FIND TODOS: Find TODO/FIXME/HACK comments in code files.",
            "params": {"directory": "string"},
            "requires_commander": False,
            "requires_verification": True
        },
        "count_lines": {
            "module": "tools.code.code_tools",
            "function": "count_lines",
            "description": "📊 COUNT LINES: Count lines of code by file type in a directory.",
            "params": {"directory": "string", "extensions": "list"},
            "requires_commander": False,
            "requires_verification": True
        },
        "find_imports": {
            "module": "tools.code.code_tools",
            "function": "find_imports",
            "description": "📦 FIND IMPORTS: Extract import statements from Python files.",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "check_syntax": {
            "module": "tools.code.code_tools",
            "function": "check_syntax",
            "description": "✅ CHECK SYNTAX: Validate Python syntax without executing code.",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": False
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
