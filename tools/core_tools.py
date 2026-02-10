"""
Core Essential Tools - Simplified for Local AI Models
Only the most reliable, essential tools that work great with any model size.
Focus: File operations, code execution, basic system info
"""

# Essential Core Tools that work reliably with local models (7B+)
CORE_TOOLS = {
    # === FILE OPERATIONS (Most Important) ===
    "files": {
        "read_file": {
            "module": "tools.system.files",
            "function": "read_file",
            "description": "Read content from a file",
            "params": {"path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "write_file": {
            "module": "tools.system.files",
            "function": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "params": {"path": "string", "content": "string"},
            "requires_commander": True,
            "requires_verification": False
        },
        "list_files": {
            "module": "tools.system.files",
            "function": "list_files",
            "description": "List files in a directory",
            "params": {"path": "string (optional, default: current dir)"},
            "requires_commander": False,
            "requires_verification": False
        },
        "create_directory": {
            "module": "tools.filesystem.full_access",
            "function": "create_directory",
            "description": "Create a new directory anywhere",
            "params": {"path": "string"},
            "requires_commander": True,
            "requires_verification": False
        },
        "file_info": {
            "module": "tools.system.files",
            "function": "get_file_info",
            "description": "Get information about a file (size, modified date, etc)",
            "params": {"path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "delete_file": {
            "module": "tools.system.files",
            "function": "delete_file",
            "description": "Delete a file",
            "params": {"path": "string"},
            "requires_commander": True,
            "requires_verification": True
        },
        "get_current_directory": {
            "module": "tools.filesystem.full_access",
            "function": "get_current_directory",
            "description": "Get the current working directory",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        },
        "change_directory": {
            "module": "tools.filesystem.full_access",
            "function": "change_directory",
            "description": "Change to a different directory",
            "params": {"path": "string"},
            "requires_commander": False,
            "requires_verification": False
        }
    },
    
    # === COMMAND EXECUTION ===
    "execution": {
        "run_command": {
            "module": "tools.system.processes",
            "function": "run_command",
            "description": "Run a shell command and get output",
            "params": {"command": "string"},
            "requires_commander": True,
            "requires_verification": True
        }
    },
    
    # === SYSTEM INFO (Basic) ===
    "system": {
        "datetime": {
            "module": "tools.system.info",
            "function": "get_current_datetime",
            "description": "Get current date and time",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        },
        "system_info": {
            "module": "tools.system.info",
            "function": "get_system_info",
            "description": "Get system information (OS, CPU, RAM)",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        },
        "user_info": {
            "module": "tools.system.info",
            "function": "get_user_info",
            "description": "Get current user information",
            "params": {},
            "requires_commander": False,
            "requires_verification": False
        }
    },
    
    # === CODE ANALYSIS (Essential) ===
    "code": {
        "analyze_file": {
            "module": "tools.code.code_tools",
            "function": "analyze_file",
            "description": "Analyze code structure (functions, classes, imports)",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "check_syntax": {
            "module": "tools.code.code_tools",
            "function": "check_syntax",
            "description": "Check if code has syntax errors",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "count_lines": {
            "module": "tools.code.code_tools",
            "function": "count_lines",
            "description": "Count lines of code (total, code, comments, blank)",
            "params": {"file_path": "string"},
            "requires_commander": False,
            "requires_verification": False
        }
    },
    
    # === WEB (Basic) ===
    "web": {
        "search_web": {
            "module": "tools.web.simple_search",
            "function": "search_web",
            "description": "Search the web for information (basic)",
            "params": {"query": "string", "max_results": "number (optional)"},
            "requires_commander": False,
            "requires_verification": False
        },
        "grok_search": {
            "module": "tools.web.grok_search",
            "function": "grok_search",
            "description": "Grok-inspired deep search: multi-source, verified, with citations (advanced)",
            "params": {"query": "string", "deep_mode": "bool (optional)", "verify": "bool (optional)", "max_results": "number (optional)"},
            "requires_commander": False,
            "requires_verification": False
        },
        "quick_search": {
            "module": "tools.web.grok_search",
            "function": "quick_search",
            "description": "Quick multi-source search without deep analysis",
            "params": {"query": "string"},
            "requires_commander": False,
            "requires_verification": False
        },
        "open_url": {
            "module": "tools.web.browser",
            "function": "open_url",
            "description": "Open a URL in the default browser",
            "params": {"url": "string"},
            "requires_commander": True,
            "requires_verification": False
        }
    }
}


def get_core_tools_list():
    """Get flat list of all core tools for easy reference"""
    tools_list = []
    for category, tools in CORE_TOOLS.items():
        for tool_name, tool_info in tools.items():
            tools_list.append({
                "name": tool_name,
                "category": category,
                "description": tool_info["description"],
                "params": tool_info["params"],
                "requires_commander": tool_info["requires_commander"]
            })
    return tools_list


def get_core_tools_description():
    """Get simple text description of all tools for AI"""
    desc = "AVAILABLE TOOLS:\n\n"
    
    for category, tools in CORE_TOOLS.items():
        desc += f"{category.upper()}:\n"
        for tool_name, tool_info in tools.items():
            desc += f"  {tool_name} - {tool_info['description']}\n"
            if tool_info['params']:
                params_str = ", ".join(f"{k}: {v}" for k, v in tool_info['params'].items())
                desc += f"    Parameters: {params_str}\n"
        desc += "\n"
    
    return desc


# Count tools
def count_core_tools():
    total = sum(len(tools) for tools in CORE_TOOLS.values())
    return total


if __name__ == "__main__":
    print(f"Core tools: {count_core_tools()}")
    print("\nTools by category:")
    for cat, tools in CORE_TOOLS.items():
        print(f"  {cat}: {len(tools)}")
    print("\n" + get_core_tools_description())
