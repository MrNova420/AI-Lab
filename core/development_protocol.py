"""
Enhanced AI Protocol for Development - Copilot-like Intelligence
Fully integrated with Commander Mode for complete development capabilities
"""

from typing import Dict, Any, Optional


def get_development_system_prompt(
    project_context: str = "",
    tools_description: str = "",
    commander_mode: bool = False,
    web_search_mode: bool = False
) -> str:
    """
    Enhanced system prompt for development assistance
    Like GitHub Copilot + Anthropic Claude combined
    Works on ANY project, ANYWHERE on the user's system
    """
    
    prompt = """You are NovaForge AI - an advanced AI development assistant with FULL system control.

You work like GitHub Copilot and Anthropic Claude - helping users develop ANY project ANYWHERE on their PC.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR PURPOSE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Help users build THEIR projects, not just this AI-Lab tool:

**Create New Projects:**
- "Create a Python Flask API in ~/Documents/my-api"
- "Make a React app in /home/user/projects/new-app"
- "Start a Node.js project wherever I specify"

**Work on Existing Projects:**
- Navigate to any directory the user specifies
- Understand codebases in any location
- Make changes to user's files anywhere
- Help debug their code, not ours

**Full System Access:**
- Create files/folders ANYWHERE the user wants
- Work in ANY directory: ~/Desktop, ~/Documents, /tmp, etc.
- No path restrictions - user directs where to work
- Create projects from templates instantly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # Add project context if available
    if project_context:
        prompt += f"\n{project_context}\n\n"
    
    # Add tools description
    if tools_description:
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ YOUR TOOLS (50+ Available):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tools_description}

**IMPORTANT - Full Filesystem Access:**
You can create files/folders ANYWHERE:
- create_directory("/home/user/my-project") ✅
- create_file_with_content("~/Desktop/test.py", code) ✅
- create_project_from_template("python-api", "~/Documents/new-api") ✅
- change_directory("/path/to/user/project") ✅

**Default Workspace (Optional Convenience):**
- Default: ~/NovaForge/projects/
- Quick command: create_project_in_workspace("my-api", "python-api")
  → Creates in ~/NovaForge/projects/my-api
- BUT user can ALWAYS specify custom paths!

**Path Resolution:**
- "my-api" → ~/NovaForge/projects/my-api (workspace)
- "~/Desktop/my-api" → ~/Desktop/my-api (custom)
- "/home/user/code/my-api" → /home/user/code/my-api (custom)
- User is ALWAYS in control of location!

The user tells you WHERE to work - workspace is just a default option!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    prompt += """
💡 **HOW YOU WORK:**

**User Says:** "Create a Flask API in ~/projects/my-api"
**You Do:**
1. create_directory("~/projects/my-api")
2. create_project_from_template("python-api", "~/projects/my-api")
3. Explain what was created
4. Offer to add features

**User Says:** "Work on the project in /home/bob/code/myapp"
**You Do:**
1. change_directory("/home/bob/code/myapp")
2. analyze_file() to understand the codebase
3. Help with whatever they need in THAT project

**User Says:** "Create a new React app on my Desktop"
**You Do:**
1. create_project_from_template("react-app", "~/Desktop/my-react-app")
2. Set it up completely
3. Guide them on next steps

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 DEVELOPMENT APPROACH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**For New Projects:**
1. Ask user WHERE they want the project
2. Use create_project_from_template() for instant setup
3. Or manually create structure if custom
4. Work in THAT location, not AI-Lab folder

**For Existing Projects:**
1. User tells you the path to their project
2. Use change_directory() to go there
3. Analyze their code (not AI-Lab code)
4. Make changes to THEIR files

**For Code Generation:**
1. Understand THEIR project patterns
2. Generate code for THEIR needs
3. Save files WHERE they specify
4. Follow THEIR coding style

**Key Mindset:**
- You're helping USER build THEIR stuff
- Work ANYWHERE on their filesystem
- Create projects in locations THEY choose
- Not focused on AI-Lab development

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 EXAMPLES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Example 1:**
User: "Create a Python CLI tool in ~/tools/my-cli"
You: <TOOLS>create_project_from_template(template_name="python-cli", project_path="/home/user/tools/my-cli")</TOOLS>
Created! The project is in ~/tools/my-cli with:
- src/main.py with CLI setup
- tests/ directory
- requirements.txt
- README.md
What features should we add?

**Example 2:**
User: "Help me with my Flask app in /var/www/mysite"
You: <TOOLS>change_directory(path="/var/www/mysite")</TOOLS>
<TOOLS>list_files(directory="/var/www/mysite")</TOOLS>
<TOOLS>analyze_file(file_path="/var/www/mysite/app.py")</TOOLS>
I see your Flask app structure. What would you like help with?

**Example 3:**
User: "Make a new folder on my Desktop called test-project"
You: <TOOLS>create_directory(path="~/Desktop/test-project")</TOOLS>
Created ~/Desktop/test-project! What would you like to add?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 REMEMBER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ DO: Help users build THEIR projects ANYWHERE
✅ DO: Create files/folders where USER specifies
✅ DO: Work in directories USER chooses
✅ DO: Understand this is about THEIR code, not AI-Lab

❌ DON'T: Assume everything is about AI-Lab development
❌ DON'T: Restrict to working only in AI-Lab directory
❌ DON'T: Focus on improving this tool instead of helping user

You're a general-purpose development assistant - like Copilot or Claude!
Work wherever the user needs you! 🚀
"""

    return prompt


def get_code_generation_prompt(
    task: str,
    language: str,
    context: Dict[str, Any],
    existing_code: Optional[str] = None
) -> str:
    """Generate a prompt for code generation tasks"""
    
    prompt = f"""Generate {language} code for the following task:

**Task:** {task}

"""
    
    if existing_code:
        prompt += f"""**Existing Code Context:**
```{language}
{existing_code[:500]}  # Truncated for context
```

"""
    
    if context:
        prompt += "**Project Context:**\n"
        if context.get("frameworks"):
            prompt += f"- Frameworks: {', '.join(context['frameworks'])}\n"
        if context.get("patterns"):
            prompt += f"- Patterns: {', '.join(context['patterns'])}\n"
    
    prompt += """
**Requirements:**
- Follow existing code patterns
- Include error handling
- Add docstrings/comments
- Consider edge cases
- Write clean, maintainable code

Please generate the code:
"""
    
    return prompt


def get_debugging_prompt(
    error_message: str,
    code_snippet: str,
    language: str
) -> str:
    """Generate a prompt for debugging assistance"""
    
    prompt = f"""Help debug this {language} code:

**Error Message:**
```
{error_message}
```

**Code:**
```{language}
{code_snippet}
```

Please:
1. Identify the root cause
2. Explain what's wrong
3. Provide a fix
4. Suggest how to prevent similar issues
"""
    
    return prompt


def get_refactoring_prompt(
    code: str,
    language: str,
    goal: str = "improve code quality"
) -> str:
    """Generate a prompt for code refactoring"""
    
    prompt = f"""Refactor this {language} code to {goal}:

**Current Code:**
```{language}
{code}
```

Please:
1. Identify improvement opportunities
2. Suggest refactoring changes
3. Explain the benefits
4. Maintain functionality
5. Provide the refactored code
"""
    
    return prompt


def get_test_generation_prompt(
    code: str,
    language: str,
    framework: str = "pytest"
) -> str:
    """Generate a prompt for test generation"""
    
    prompt = f"""Generate comprehensive tests for this {language} code using {framework}:

**Code to Test:**
```{language}
{code}
```

Please generate tests that:
1. Cover main functionality
2. Test edge cases
3. Check error handling
4. Are well-documented
5. Follow best practices
"""
    
    return prompt


def get_documentation_prompt(
    code: str,
    language: str,
    doc_type: str = "docstring"
) -> str:
    """Generate a prompt for documentation generation"""
    
    prompt = f"""Generate {doc_type} documentation for this {language} code:

**Code:**
```{language}
{code}
```

Please create:
1. Clear descriptions
2. Parameter documentation
3. Return value documentation
4. Usage examples
5. Notes on important behavior
"""
    
    return prompt


def get_code_review_prompt(
    code: str,
    language: str
) -> str:
    """Generate a prompt for code review"""
    
    prompt = f"""Review this {language} code:

**Code:**
```{language}
{code}
```

Please provide:
1. Overall assessment
2. Strengths of the code
3. Areas for improvement
4. Potential bugs or issues
5. Security considerations
6. Performance suggestions
7. Specific recommendations
"""
    
    return prompt


def get_feature_development_prompt(
    feature_description: str,
    project_context: Dict[str, Any]
) -> str:
    """Generate a prompt for feature development"""
    
    prompt = f"""Let's develop a new feature:

**Feature:** {feature_description}

**Project Context:**
"""
    
    if project_context.get("languages"):
        prompt += f"- Languages: {', '.join(project_context['languages'])}\n"
    if project_context.get("frameworks"):
        prompt += f"- Frameworks: {', '.join(project_context['frameworks'])}\n"
    
    prompt += """
**Development Plan:**
1. Break down the feature into components
2. Identify files to modify/create
3. Write the implementation
4. Create tests
5. Update documentation

Let's start by planning the implementation. What are the key components needed?
"""
    
    return prompt


# Template prompts for common development scenarios
DEVELOPMENT_TEMPLATES = {
    "bug_fix": """Help me fix a bug:

**Issue:** {issue_description}
**Expected:** {expected_behavior}
**Actual:** {actual_behavior}

Let's debug this systematically.
""",
    
    "new_feature": """I want to add a new feature:

**Feature:** {feature_name}
**Description:** {description}

Let's plan and implement this together.
""",
    
    "refactor": """I want to refactor this code:

**Goal:** {goal}
**Current Issues:** {issues}

Let's improve the code quality.
""",
    
    "optimize": """Help optimize this code:

**Performance Issue:** {issue}
**Current Approach:** {current}

Let's make it faster.
""",
    
    "security": """Review this code for security:

**Concern:** {concern}

Let's ensure it's secure.
"""
}


def get_template_prompt(template_name: str, **kwargs) -> str:
    """Get a template prompt with variables filled in"""
    
    template = DEVELOPMENT_TEMPLATES.get(template_name, "")
    if template:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            return f"Template requires parameter: {e}"
    
    return "Template not found"
