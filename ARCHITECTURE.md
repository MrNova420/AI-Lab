# NovaForge AI Architecture - Analysis & Intelligence System

## 🎯 PHILOSOPHY

**The AI doesn't just execute commands - it ANALYZES, THINKS, and DECIDES**

### Two Modes:

**1. Normal Mode (Safe)**
- ✅ Can chat normally
- ✅ Can analyze system (read-only)
- ✅ Can search web
- ❌ Cannot control PC (no mouse/keyboard/apps)

**2. Commander Mode (Full Access)**
- ✅ Everything from Normal Mode
- ✅ PLUS full PC control
- ✅ Mouse, keyboard, apps, files
- ⚠️ User must explicitly enable

## 🧠 AI INTELLIGENCE LAYERS

### Layer 1: ANALYSIS (Always Available)
The AI can understand its environment:
- `analyze_system()` - Get OS, version, architecture
- `check_running()` - See what processes are active
- `check_app(name)` - Verify if app is installed
- `list_apps()` - Get common installed applications
- `analyze_result(cmd, result)` - Understand success/failure

### Layer 2: DECISION MAKING
Based on analysis, AI decides:
- Does user want ACTION or INFO?
- Is the requested app installed?
- Should I open app or website?
- Did the previous action succeed?

### Layer 3: ACTION (Commander Mode Only)
After analyzing and deciding, AI can act:
- Open/close applications
- Control mouse and keyboard
- Take screenshots
- Manage files

### Layer 4: VERIFICATION
After acting, AI verifies:
- Did the action succeed?
- If failed, what went wrong?
- What should we try instead?

## 📁 ARCHITECTURE

```
ai-forge/
├── core/
│   └── ai_protocol.py          # AI behavior instructions
│
├── tools/
│   ├── __init__.py             # Tools registry
│   │
│   ├── system/
│   │   ├── analyzer.py         # System analysis (SMART)
│   │   ├── apps.py             # App management
│   │   └── screenshot.py       # Screen capture
│   │
│   ├── input/
│   │   ├── mouse.py            # Mouse control
│   │   └── keyboard.py         # Keyboard control
│   │
│   └── web/
│       ├── browser.py          # Open URLs
│       └── search.py           # Web search
│
└── scripts/
    ├── commander.py            # Low-level system bridge
    ├── intent_parser.py        # Parse natural language
    └── api_server.py           # HTTP API
```

## 🎭 EXAMPLE FLOW

### User: "Open Steam"

**Step 1: AI Receives Request**
```
AI thinks: "User wants to open Steam. Let me analyze first..."
```

**Step 2: ANALYSIS (AI uses tools)**
```python
# AI internally checks:
result = check_app("steam")
# Result: {"exists": True, "status": "FOUND_INSTALLED"}
```

**Step 3: AI DECIDES**
```
AI thinks: "Steam is installed! I'll open the desktop app."
AI responds: "Sure! I'll open Steam for you now..."
```

**Step 4: BACKEND EXECUTES**
```python
# Intent parser detects action needed
tools = parse_intent("open steam", ai_response)
# Returns: [{"tool": "open_app", "params": {"app": "steam"}}]

# Commander executes
commander.open_app("steam")
```

**Step 5: AI VERIFIES**
```python
# Backend checks result
result = {"success": True, "message": "Opened steam"}

# AI analyzes
analysis = analyze_result("open_app", result)
# Shows success feedback to user
```

### User: "Open Discord" (NOT installed)

**Step 1-2: Same analysis**
```python
result = check_app("discord")
# Result: {"exists": False, "status": "NOT_FOUND"}
```

**Step 3: AI DECIDES (SMART)**
```
AI thinks: "Discord isn't installed. I should offer website instead."
AI responds: "Discord isn't installed on your system, but I can open 
             the web version for you at discord.com!"
```

**Step 4: BACKEND EXECUTES**
```python
# Opens https://discord.com instead of app
tools = [{"tool": "open_url", "params": {"url": "https://discord.com"}}]
```

## 🔐 SAFETY MODEL

### Normal Mode:
```python
# User can NEVER accidentally enable dangerous tools
allowed_tools = [
    "analyze_system",     # ✅ Safe - just reading
    "check_running",      # ✅ Safe - just viewing
    "check_app",          # ✅ Safe - just checking
    "list_apps",          # ✅ Safe - just listing
    "open_url",           # ✅ Safe - just browser
    "web_search"          # ✅ Safe - just search
]
```

### Commander Mode (Requires explicit toggle):
```python
# User MUST click ⚡ Commander Mode button
additional_tools = [
    "open_app",           # ⚠️ Opens programs
    "close_app",          # ⚠️ Closes programs
    "mouse_move",         # ⚠️ Controls cursor
    "mouse_click",        # ⚠️ Clicks mouse
    "keyboard_type",      # ⚠️ Types text
    "keyboard_press",     # ⚠️ Presses keys
    "screenshot"          # ✅ Mostly safe
]
```

## 🎯 KEY ADVANTAGES

1. **AI THINKS** - Not just pattern matching, actual analysis
2. **SAFE BY DEFAULT** - Normal mode can't do anything dangerous
3. **EXPLICIT CONTROL** - User must enable Commander Mode
4. **SELF-AWARE** - AI knows what it can/can't do
5. **VERIFIABLE** - AI checks if actions succeeded
6. **ADAPTIVE** - Adjusts behavior based on system state
7. **EXTENSIBLE** - Easy to add new tools

## 📝 ADDING NEW TOOLS

### 1. Create tool file:
```python
# tools/system/mynew_tool.py
def my_new_function(param1, param2):
    """Do something smart"""
    # Implementation
    return {"success": True, "message": "Done!"}
```

### 2. Register in tools/__init__.py:
```python
"my_tool": {
    "module": "tools.system.mynew_tool",
    "function": "my_new_function",
    "description": "Does something smart",
    "params": {"param1": "string", "param2": "int"},
    "requires_commander": True  # or False if safe
}
```

### 3. Done!
The AI now has access to your new tool and will use it intelligently.

## 🚀 SUMMARY

**Before:** Hardcoded keywords, no awareness, just execution
**Now:** AI analyzes → decides → acts → verifies

The AI is now a TRUE intelligent assistant with:
- System awareness
- Decision-making ability
- Safety controls
- Result verification
- Extensible architecture

**It's not just a command executor - it's an intelligent system controller!**
