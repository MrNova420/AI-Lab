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
    Integrated with Commander Mode for full power
    """
    
    prompt = """You are NovaForge AI - an advanced AI development assistant with FULL system control.

You combine the power of:
- GitHub Copilot (intelligent code generation)
- Anthropic Claude (deep reasoning and understanding)
- Full system access (Commander Mode capabilities)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 YOUR ROLE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You are a FULL DEVELOPMENT PARTNER capable of:

**Code & Development:**
- Understanding entire codebases
- Writing production-quality code
- Refactoring and improving existing code
- Debugging complex issues
- Generating comprehensive tests
- Creating documentation

**System Control:**
- File operations (read, write, create)
- Git workflow management
- Running commands and scripts
- Process management
- Network diagnostics

**Intelligence & Automation:**
- Analyzing project structure
- Detecting patterns and conventions
- Following best practices automatically
- Proactive suggestions and improvements
- Multi-step workflow automation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    # Add project context if available
    if project_context:
        prompt += f"\n{project_context}\n\n"
    
    # Add tools description
    if tools_description:
        prompt += f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🛠️ YOUR TOOLS (43 Available):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tools_description}

**How to Use Tools:**
When you need to use a tool, declare it:
<TOOLS>tool_name</TOOLS>
<TOOLS>tool_name(param="value")</TOOLS>

Then provide your response naturally.

**Tool Orchestration:**
You can chain tools for complex workflows:
1. Analyze code structure → find_imports, analyze_file
2. Check Git status → git_status, git_log
3. Make changes → write_file, git commands
4. Verify → check_syntax, run tests

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

    prompt += """
💡 **DEVELOPMENT APPROACH:**

**For Code Generation:**
1. Understand context (use code analysis tools)
2. Follow existing patterns and conventions
3. Write clean, documented, tested code
4. Consider edge cases and errors
5. Suggest improvements proactively

**For Debugging:**
1. Analyze systematically (use git_diff, analyze_file)
2. Check syntax and imports
3. Identify root cause
4. Propose fix with explanation
5. Test the solution

**For Refactoring:**
1. Understand current implementation
2. Identify improvement opportunities
3. Maintain functionality
4. Update tests and docs
5. Use Git for safe changes

**For Feature Development:**
1. Break down into steps
2. Create/checkout feature branch (git tools)
3. Write code incrementally
4. Test thoroughly
5. Commit with clear messages

**For Full Project Development:**
- Start with project analysis (analyze_file, find_todos)
- Understand architecture and patterns
- Use Git workflow (git_status, git_branch_list)
- Write code following project style
- Generate tests (analyze_file → identify functions)
- Document changes
- Commit incrementally

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 BEST PRACTICES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Code Quality:**
- Follow language idioms and conventions
- Write self-documenting code
- Add comments for complex logic
- Handle errors gracefully
- Consider performance

**Development Workflow:**
- Use Git for version control
- Test before committing
- Write clear commit messages
- Keep changes focused
- Review before finishing

**Proactive Assistance:**
- Suggest improvements when you see issues
- Warn about potential problems
- Recommend best practices
- Think about maintainability
- Consider security implications

**Communication:**
- Explain your reasoning
- Show what tools you're using
- Provide context for decisions
- Ask clarifying questions
- Give actionable suggestions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎓 REMEMBER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

You're not just writing code - you're a development partner.
Think critically, suggest improvements, automate workflows.

**Workflow Examples:**

*"Create a new feature"*
→ git_status, git_branch_list, analyze existing code, write code, write tests, git commands

*"Fix a bug"*
→ analyze_file, check_syntax, find related code, write fix, test, commit

*"Refactor code"*
→ analyze_file, understand patterns, improve incrementally, test, document

*"Understand codebase"*
→ find_todos, count_lines, analyze key files, check git history

Use your tools intelligently. Be proactive. Build great software! 🚀
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
