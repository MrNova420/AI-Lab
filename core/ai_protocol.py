"""
NovaForge AI Protocol
Defines how the AI should behave and use tools intelligently
Enhanced for full development assistance (Copilot-like capabilities)
Optimized for both cloud and local models
"""

from typing import Optional

def get_system_prompt(
    commander_mode=False, 
    web_search_mode=False, 
    tools_description="",
    development_mode=True,
    project_context=None,
    use_simple_mode=True  # NEW: Use simpler prompts for local models
):
    """
    Get system prompt based on mode
    Commander Mode = Full PC access + Development assistance
    Simple Mode = Better for local models (recommended)
    Normal Mode = Safe chat only
    """
    
    # Use simple protocol for better local model compatibility
    if use_simple_mode and (commander_mode or development_mode):
        from core.simple_protocol import get_simple_development_prompt
        return get_simple_development_prompt(
            tools_description=tools_description,
            commander_mode=commander_mode
        )
    
    # Use enhanced development protocol if available (for larger models)
    if development_mode and not use_simple_mode:
        try:
            from core.development_protocol import get_development_system_prompt
            return get_development_system_prompt(
                project_context=project_context or "",
                tools_description=tools_description,
                commander_mode=commander_mode,
                web_search_mode=web_search_mode
            )
        except:
            # Fallback to original if development_protocol not available
            pass
    
    if commander_mode or web_search_mode:
        return get_commander_prompt(tools_description)
    else:
        return get_normal_prompt()


def get_normal_prompt():
    """Safe AI chat mode - no system control"""
    return """You are NovaForge AI Assistant - a helpful, friendly AI.

You can:
- Answer questions
- Have conversations
- Provide information
- Help with problem-solving

You currently DO NOT have system control tools.
You are in SAFE MODE - just a conversational AI assistant.

Be helpful, friendly, and informative!
"""


def get_commander_prompt(tools_description=""):
    """Full AI Commander mode - with system access"""
    
    base_prompt = """You are NovaForge AI - an intelligent assistant.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧠 TOOL USAGE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

When you need tools, declare them:
<TOOLS>tool_name</TOOLS>
<TOOLS>tool_name(param="value")</TOOLS>

Then respond naturally.

**IMPORTANT RULES:**
1. Use datetime tool for ANY date/time question
2. Use system_info for system questions
3. ONLY use tools when user asks for info/action
4. If just chatting, NO tools needed

**EXAMPLES:**

User: "What's today?"
You: <TOOLS>datetime</TOOLS>
Let me check the date and time.

User: "What's my system?"
You: <TOOLS>system_info</TOOLS>
Checking your system information.

User: "How are you?"
You: I'm doing great! How can I help?
(No tools - just chat)
"""
    
    if tools_description:
        base_prompt += f"\n{tools_description}\n"
    
    base_prompt += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**BE CONCISE.** Don't over-explain. Use tools when needed, chat naturally otherwise.

**FOR DEVELOPMENT TASKS:**
- Analyze code using code analysis tools
- Use Git tools to understand changes
- Write clean, documented code
- Think about testing and quality
- Be proactive with suggestions
"""
    
    return base_prompt


def inject_project_context(prompt: str, project_root: str) -> str:
    """Inject project context into prompt for better understanding"""
    try:
        from core.project_context import get_ai_context
        context = get_ai_context(project_root)
        
        # Insert context near the beginning
        insertion_point = prompt.find("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        if insertion_point > 0:
            return prompt[:insertion_point] + f"\n{context}\n\n" + prompt[insertion_point:]
        else:
            return f"{context}\n\n{prompt}"
    except Exception as e:
        # If context injection fails, return original prompt
        return prompt
