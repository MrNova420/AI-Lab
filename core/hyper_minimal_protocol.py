"""
Hyper-Minimal Protocol - For Ultra-Small Models (1B+)
Works with: Qwen 1.8B, Phi-1, TinyLlama 1.1B, etc.

Philosophy: Absolute minimum. Single steps only.
"""


def get_hyper_minimal_prompt(commander_mode: bool = False) -> str:
    """
    The smallest possible prompt for 1B models.
    Ultra-simple, single-step focused.
    """
    
    if not commander_mode:
        return """You help users. Be brief."""
    
    # Commander Mode - ultra-ultra simple for 1B models
    return """You help users with files and commands.

TOOLS (9):
read_file(path) - read file
write_file(path, content) - write file
create_directory(path) - make folder
run_command(command) - run command
check_app(app_name) - check if app exists
open_app(app_name) - open app
open_url(url) - open website
search_web(query) - search internet
list_files(path) - list files

HOW:
<TOOLS>tool_name(param="value")</TOOLS>

EXAMPLES:
User: "read test.py"
You: <TOOLS>read_file(path="test.py")</TOOLS>

User: "create file.txt with hello"
You: <TOOLS>write_file(path="file.txt", content="hello")</TOOLS>

User: "search AI"
You: <TOOLS>search_web(query="AI")</TOOLS>

RULES:
- One tool at a time
- Keep it simple
- Show results"""


def get_1b_model_examples():
    """
    Specific examples for 1B models
    """
    return {
        'read': '<TOOLS>read_file(path="file.txt")</TOOLS>',
        'write': '<TOOLS>write_file(path="test.py", content="print(1)")</TOOLS>',
        'search': '<TOOLS>search_web(query="python")</TOOLS>',
        'command': '<TOOLS>run_command(command="ls")</TOOLS>',
        'open': '<TOOLS>open_url(url="https://google.com")</TOOLS>'
    }
