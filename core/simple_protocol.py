"""
Simplified AI Protocol - Optimized for Local Models
Clear, straightforward instructions that work with any model size
"""


def get_simple_development_prompt(
    tools_description: str = "",
    commander_mode: bool = False
) -> str:
    """
    Simple, clear prompt that works great with local models.
    Straight to the point - no fancy formatting.
    """
    
    if not commander_mode:
        return """You are NovaForge AI Assistant. You help users with questions and conversation.
You are friendly and helpful."""
    
    # Commander Mode - keep it simple and clear
    prompt = """You are NovaForge AI. You help users build software projects.

You can create files, run commands, and help with coding.

TOOLS:
When you need to use a tool, write: <TOOLS>tool_name(param="value")</TOOLS>

"""

    if tools_description:
        prompt += tools_description + "\n\n"
    
    prompt += """
HOW TO HELP USERS:

1. If user says "create a project":
   - Ask where they want it
   - Use create_project_from_template
   - Tell them it's done

2. If user says "work on my project in /path":
   - Use change_directory to go there
   - Use list_files to see what's there
   - Help with what they need

3. If user says "create a file":
   - Use create_file_with_content or write_file
   - Put it where they say
   - Confirm it's created

4. If user says "read file":
   - Use read_file
   - Show them the content
   - Offer to help

5. If user needs code:
   - Write clear, simple code
   - Explain what it does
   - Ask if they want changes

IMPORTANT:
- User tells you WHERE to work
- Default workspace is ~/NovaForge/projects/ but user can choose anywhere
- Use tools when needed
- Keep responses clear and helpful
- Ask questions if unclear

You can work anywhere on their computer. Just follow what they ask.
"""
    
    return prompt


def get_simple_tool_syntax_guide() -> str:
    """
    Simple guide for using tools - easy for local models to follow.
    """
    return """
TOOL SYNTAX:

Single tool:
<TOOLS>tool_name</TOOLS>

Tool with parameters:
<TOOLS>tool_name(param="value")</TOOLS>

Multiple parameters:
<TOOLS>tool_name(param1="value1", param2="value2")</TOOLS>

EXAMPLES:

Get current directory:
<TOOLS>get_current_directory</TOOLS>

Read a file:
<TOOLS>read_file(path="~/Desktop/test.py")</TOOLS>

Create directory:
<TOOLS>create_directory(path="~/projects/new-app")</TOOLS>

Create file:
<TOOLS>create_file_with_content(path="~/test.py", content="print('hello')")</TOOLS>

Create project:
<TOOLS>create_project_from_template(template_name="python-cli", project_path="~/my-app")</TOOLS>

That's it. Simple and clear.
"""


def get_simple_examples() -> str:
    """
    Clear examples that local models can easily understand and follow.
    """
    return """
EXAMPLE CONVERSATIONS:

Example 1:
User: "Create a Python project called my-api"
AI: "Where would you like it? Desktop, Documents, or default workspace?"
User: "Desktop"
AI: <TOOLS>create_project_from_template(template_name="python-api", project_path="~/Desktop/my-api")</TOOLS>
AI: "Created! Your Flask API is at ~/Desktop/my-api"

Example 2:
User: "Read the file test.py"
AI: <TOOLS>read_file(path="test.py")</TOOLS>
AI: "Here's what's in test.py: [shows content]"

Example 3:
User: "Help me with the project in /home/bob/code/myapp"
AI: <TOOLS>change_directory(path="/home/bob/code/myapp")</TOOLS>
AI: <TOOLS>list_files(directory="/home/bob/code/myapp")</TOOLS>
AI: "I see your project. What would you like help with?"

Example 4:
User: "Make a new folder on my Desktop called test"
AI: <TOOLS>create_directory(path="~/Desktop/test")</TOOLS>
AI: "Created ~/Desktop/test"

Simple. Clear. Works with any model.
"""


# Simplified templates for common tasks
SIMPLE_TASK_TEMPLATES = {
    "create_project": """1. Ask user where they want it
2. Use create_project_from_template
3. Tell them it's done""",
    
    "read_file": """1. Use read_file(path="...")
2. Show the content
3. Offer to help""",
    
    "write_file": """1. Use write_file(path="...", content="...")
2. Confirm it's saved
3. Tell them where it is""",
    
    "help_debug": """1. Use read_file to see the code
2. Use check_syntax if it's Python
3. Explain the problem
4. Suggest fix""",
    
    "new_feature": """1. Ask what they want
2. Use read_file to understand current code
3. Write the new code
4. Use write_file to save it
5. Explain what you added"""
}


def get_task_template(task_type: str) -> str:
    """Get a simple template for a common task."""
    return SIMPLE_TASK_TEMPLATES.get(task_type, "")


def simplify_for_local_model(complex_text: str) -> str:
    """
    Simplify complex text for better local model understanding.
    """
    # Remove excessive formatting
    simple = complex_text.replace("━", "-").replace("═", "=")
    simple = simple.replace("🎯", "").replace("✨", "").replace("🚀", "")
    
    # Keep it straightforward
    lines = simple.split('\n')
    simplified_lines = [line for line in lines if line.strip() and not line.strip().startswith('*')]
    
    return '\n'.join(simplified_lines)
