# 🛠️ NovaForge AI Lab - Current Tools & Capabilities

**Last Updated:** February 6, 2026

## 📊 Overview

The AI has **21 tools** across 3 categories:
- **System Tools**: 14 tools (5 always available, 9 require Commander mode)
- **Web Tools**: 4 tools (1 always available, 3 require Web Search mode)
- **Input Tools**: 4 tools (all require Commander mode)

---

## 🔓 ALWAYS AVAILABLE (Normal Mode)

### 📅 Date/Time Tools

**`current_date()`**
- Get today's date
- Returns: Formatted date like "Friday, February 06, 2026"
- Example: "What's today's date?"

**`current_time()`**
- Get current time
- Returns: Time like "11:30 PM"
- Example: "What time is it?"

**`current_datetime()`**
- Get both date and time
- Returns: "Friday, February 06, 2026 at 11:30 PM"
- Example: "What's the current date and time?"

### 💻 System Information

**`system_info()`**
- Get OS, version, architecture
- Returns: "System: Linux 5.15.0 on x86_64"
- Example: "What system am I running?"

**`user_info()`**
- Get current user details
- Returns: Username and home directory
- Example: "Who am I logged in as?"

**`analyze_system()`**
- Comprehensive system analysis
- Returns: Detailed OS and hardware info
- Example: "Analyze my system"

**`check_running()`**
- See what processes are running
- Returns: List of active processes
- Example: "What's running on my system?"

**`check_app(app_name)`**
- Check if an app is installed
- Parameters: `app_name` (string)
- Example: "Is Steam installed?"

**`list_apps()`**
- Get list of common installed apps
- Returns: Available applications
- Example: "What apps do I have?"

**`analyze_result(command, result)`**
- Analyze command results
- Parameters: `command` (string), `result` (dict)
- Returns: Success/failure analysis

**`open_url(url)`**
- Open a website in browser
- Parameters: `url` (string)
- Example: "Open YouTube"

---

## ⚡ COMMANDER MODE TOOLS

**Enable with the ⚡ button in Voice/Chat interface**

### 📸 Screen Capture

**`screenshot()`**
- Capture screen
- Saves to exports/
- Example: "Take a screenshot"

### 🖥️ Application Management

**`open_app(app)`**
- Open desktop application
- Parameters: `app` (string)
- Example: "Open Steam"

**`close_app(app)`**
- Close running application
- Parameters: `app` (string)
- Example: "Close Chrome"

### 🖱️ Mouse Control

**`mouse_move(x, y)`**
- Move cursor to coordinates
- Parameters: `x` (int), `y` (int)
- Example: "Move mouse to 500, 300"

**`mouse_click(button, double)`**
- Click mouse button
- Parameters: `button` ("left"/"right"/"middle"), `double` (bool)
- Example: "Click left mouse button"

### ⌨️ Keyboard Control

**`keyboard_type(text)`**
- Type text
- Parameters: `text` (string)
- Example: "Type hello world"

**`keyboard_press(key)`**
- Press special key
- Parameters: `key` (string: ENTER, ESC, TAB, etc.)
- Example: "Press enter"

---

## 🌐 WEB SEARCH MODE TOOLS

**Enable with the 🌐 button in Voice/Chat interface**

**`web_search(query, max_results)`** 🌐⚡
- **Multi-source web search across ALL major engines**
- Searches: Google, Bing, DuckDuckGo, Brave simultaneously
- Parameters: `query` (string), `max_results` (int, default=10)
- Returns: Ranked results with titles, URLs, snippets, and source info
- Example: "Search for latest AI news" → Results from all 4 engines
- **ALWAYS use this for web searches - most comprehensive!**

**`deep_research(query, max_results, scrape_top)`** 🔬
- **Comprehensive research with web scraping + analysis**
- Multi-source search + scrapes top pages + quality analysis
- Parameters: `query`, `max_results` (default=15), `scrape_top` (default=5)
- Returns: Search results + full scraped content + quality scores
- Example: "Research quantum computing advances"
- **Use for in-depth research needing detailed information**

**`fact_check(claim)`** ✓
- **Quick fact verification across multiple sources**
- Checks: Google, Bing, DuckDuckGo for consensus
- Parameters: `claim` (string to verify)
- Returns: Verification status + evidence + source count
- Example: fact_check("Python was created in 1991")
- **Use for verifying claims and checking facts**

**`scrape_webpage(url)`** 📄
- **Extract clean text from any webpage**
- Removes ads/navigation, returns main content only
- Parameters: `url` (string)
- Returns: Title + clean text content
- Example: scrape_webpage("https://python.org")
- **Use for reading full articles or documentation**

**`scrape_multiple(urls)`** 📚
- **Batch scrape multiple pages in parallel**
- Fast parallel extraction from multiple URLs at once
- Parameters: `urls` (list of strings)
- Returns: Content from all pages
- Example: scrape_multiple(["url1", "url2", "url3"])

---

## 🎯 How AI Uses Tools

The AI **intelligently decides** which tools to use based on:

1. **User Intent Analysis**: What does the user really want?
2. **Available Tools**: What can I do in current mode?
3. **Context**: Is this an info query or action request?
4. **Smart Execution**: Execute and verify results

### Example Flow:

```
User: "What's today's date?"

AI Thinks:
- User wants current date
- I see current_date() tool available
- This doesn't need Commander mode
- I'll use it

AI Declares: <TOOLS>current_date</TOOLS>
System Executes: Returns "Friday, February 06, 2026"
AI Responds: "Today is Friday, February 6th, 2026"
```

---

## 🧠 Smart Features

### Self-Correction
AI sees tool results before final response and corrects itself if wrong.

### No Hardcoding
AI reads tool descriptions and decides dynamically - no keyword matching!

### Mode-Aware
AI only uses tools available in current mode (Normal/Commander/Web Search).

### Safe by Default
Destructive actions require Commander mode explicitly enabled.

---

## 📝 Tool Implementation Status

| Tool Category | Implemented | Tested | Notes |
|--------------|-------------|--------|-------|
| Date/Time | ✅ | ✅ | Fully working |
| System Info | ✅ | ✅ | Fully working |
| Screenshots | ✅ | ⚠️ | Needs testing |
| App Control | ✅ | ⚠️ | Needs testing |
| Mouse/Keyboard | ✅ | ⚠️ | Commander.py implemented |
| Web Search | ✅ | ⚠️ | Backend ready, needs integration |

---

## 🚀 Adding New Tools

Want to add a tool? It's easy!

1. **Create the function** in `tools/system/` or `tools/web/`
2. **Register it** in `tools/__init__.py`:

```python
"my_tool": {
    "module": "tools.system.my_module",
    "function": "my_function",
    "description": "What this tool does",
    "params": {"param1": "string"},
    "requires_commander": False
}
```

3. **AI automatically discovers and uses it!**

No code changes needed in AI logic - it reads the registry dynamically!

---

## 🔮 Planned Tools

- [ ] File operations (create, read, write, delete)
- [ ] Process management (start, stop, monitor)
- [ ] Window management (switch, minimize, maximize)
- [ ] Clipboard operations
- [ ] System commands (shutdown, restart, sleep)
- [ ] Network operations (ping, download, upload)
- [ ] Calendar & reminders
- [ ] Email integration
- [ ] More web sources (Brave, SearX, Wikipedia)

---

**Total Capabilities:** 21 tools and growing! 🚀
