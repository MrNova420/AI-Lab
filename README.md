# 🧠 NovaForge AI Lab

**An intelligent, self-correcting AI assistant with voice control and system automation capabilities.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Electron](https://img.shields.io/badge/Electron-Latest-47848F.svg)](https://www.electronjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎉 Recent Updates (February 9, 2026)

### ✅ Complete Session & User Management System!

The project now includes professional-grade session and user management:

**Latest Features:**
- ✨ **NEW**: Complete session management with unlimited conversation history
- ✨ **NEW**: Session browser UI with search, filter, and export
- ✨ **NEW**: Smart session resumption (auto-resume if < 30 minutes)
- ✨ **NEW**: Multi-user system with preferences and statistics
- ✨ **NEW**: Tool tracking and analytics in Dashboard
- ✨ **NEW**: 7 additional tools (file operations, process management)
- 🔧 **FIXED**: All 28 PR review comments resolved
- 🔐 **SECURITY**: Zero vulnerabilities (CodeQL validated)

**Session Features:**
- 💾 Unlimited message history (no 100-message limit!)
- 📚 Browse and load any past conversation
- 🔍 Search and filter sessions
- 📤 Export conversations with full metadata
- 🔄 Auto-save every 5 seconds
- ⏱️ Smart timeout (fresh session after 30 min inactivity)

**Read More:**
- [Complete Project Status](PROJECT_COMPLETE.md)
- [Tool Execution System](docs/TOOL_EXECUTION_SYSTEM.md)
- [Future Enhancements](FUTURE_ENHANCEMENTS.md)
- [PR Review Implementation](PR_REVIEW_IMPLEMENTATION.md)

---

## ✨ Features

### 🧠 **Intelligent AI System**
- **Self-Correcting AI**: Uses real-world data to verify and correct responses
- **Smart Tool Selection**: AI analyzes intent and chooses appropriate tools (no hardcoded keywords!)
- **Tool Awareness**: Sees tool results before providing final answers
- **Reasoning & Learning Layer**: Context-aware system that learns from interactions
- **Smart Caching**: 30-120x speedup with intelligent cache management
- **Session Management**: Unlimited conversation history with smart resumption
- **User System**: Multi-user support with preferences and statistics
- **Dynamic Tool Registry**: 28 tools across 3 categories (expandable)

### 🎤 **Voice Assistant**
- Natural voice commands using Web Speech API
- Real-time speech-to-text transcription
- Text-to-speech responses
- Works in browser (no WSL audio issues!)

### ⚡ **Commander Mode**
- Full system control from voice/text commands
- Mouse & keyboard automation
- Application management (open, close, switch)
- Screenshot capture
- WSL → PowerShell bridge for Windows control

### 🌐 **Web Search**
- Multi-source web search integration
- Information verification and fact-checking
- Deep search with aggregation

### 🖥️ **Desktop Application**
- Built with Electron + React + Vite
- Modern, responsive UI with 4 main pages
- Voice and text chat interfaces
- Dashboard with tool statistics
- Session browser with full history
- Model and project management
- Tool execution indicators (🛠️ TOOLS, ⚡ CMD, 🌐 WEB)

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Ollama (for AI models)
- WSL (if on Windows)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
```

2. **Run setup:**
```bash
./setup.sh
```

3. **Start the application:**
```bash
./forge-app.sh
```

The app will open in your browser at `http://localhost:5173`

## 📖 Usage

### Voice Chat
1. Open the Voice page
2. Select your microphone
3. Enable Commander Mode (⚡ button) for system control
4. Start recording and speak your command!

**Example Commands:**
- "What's today's date?"
- "Open Steam"
- "Take a screenshot"
- "Search the web for AI news"

### Text Chat
1. Go to the Chat page
2. Toggle modes as needed:
   - ⚡ **Commander**: System control enabled
   - 🌐 **Web Search**: Internet search enabled
3. Type your message and watch the AI work!
4. Use **✨ New** to start fresh session
5. Use **📋 Sessions** to browse past conversations
6. Sessions auto-resume if < 30 minutes old

### Session Management
1. Click **📋 Sessions** in Chat or visit Sessions page
2. Browse all past conversations
3. Click any session to load and continue
4. Export conversations for backup/analysis
5. Search and filter by content or type

## 🏗️ Architecture

### Core Components

```
ai-forge/
├── app/                    # Electron desktop app
│   ├── main/              # Electron main process
│   ├── preload/           # Preload scripts
│   └── renderer/          # React frontend
├── core/                  # Core Python backend
│   ├── ai_protocol.py    # AI behavior and prompts
│   ├── reasoning.py      # Reasoning & learning layer
│   ├── tool_executor.py  # ✨ NEW! Dynamic tool execution engine
│   ├── runtime/          # Model runtime management
│   └── config.py         # Configuration management
├── scripts/              # Backend services
│   ├── api_server.py     # HTTP API server (REWRITTEN!)
│   ├── commander.py      # System control
│   └── smart_parser.py   # Tool declaration parser
├── tools/                # Tool registry (28 tools)
│   ├── __init__.py       # Dynamic tool registry
│   ├── system/           # System tools (datetime, apps, files, processes, screenshots)
│   ├── input/            # Mouse & keyboard control
│   └── web/              # Web tools (search, verify, scrape)
├── memory/               # Data storage
│   ├── sessions/         # Session history (unlimited)
│   └── users/            # User data
├── tests/                # Test suite
└── docs/                 # ✨ NEW! Complete documentation
```

### How It Works (Updated Architecture)

1. **User Input** → Voice or text query
2. **Mode Detection** → Normal / Commander ⚡ / Web Search 🌐
3. **AI Analysis** → AI reads tool registry and decides which tools to use
4. **Tool Declaration** → AI declares: `<TOOLS>tool_name(params)</TOOLS>`
5. **Smart Parser** → Extracts tool declarations and parameters
6. **Permission Check** → Validates tools against mode permissions
7. **Tool Execution** → Dynamically loads and runs tools from registry
8. **Result Verification** → Formats results for AI and user
9. **Final Response** → AI sees tool results and provides natural answer
10. **Display** → Streams clean output with tool indicators
7. **Result Verification** → Confidence scoring and error detection
8. **Self-Correction** → AI sees results and provides accurate answer
9. **Learning** → System tracks success rates and execution times
10. **Display** → Clean output with tool results and cache indicators

## 🛠️ Available Tools

**28 tools across 3 categories** - See [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md) for full documentation.

### Information Tools (Always Available)
- `datetime` - Get current date/time with timezone
- `system_info` - Real system information (OS, CPU, RAM, kernel)
- `user_info` - User details (username, home directory, shell)
- `check_app` - Check if application is installed

### Commander Tools (Requires ⚡ Mode)
- `open_app` / `close_app` / `switch_to_application` - Application management
- `screenshot` / `take_screenshot` - Screen capture
- `mouse_move` / `mouse_click` - Mouse control
- `keyboard_type` / `keyboard_press` / `press_combo` - Keyboard automation
- `analyze_system` - System diagnostics
- `read_file` / `write_file` / `list_files` / `file_info` - File operations (path-restricted)
- `list_processes` / `process_info` / `find_process` - Process management

### Web Tools (Requires 🌐 Mode)
- `web_search` - Multi-source internet search
- `verify_info` - Fact-checking and verification
- `open_url` - Open websites in browser

## 🧪 Testing

```bash
# Test the AI system
python test_modes.py

# Test commander functionality
python test_commander.py

# Run full test suite
pytest
```

## 🎯 Key Features in Detail

### 🧠 Reasoning & Learning Layer

The system learns and adapts from every interaction:

**Context Memory:**
- Tracks last 20 tool executions
- Maintains 50 conversation turns
- Stores user preferences
- Session persistence (survives restarts)

**Smart Caching:**
- Tool-specific cache timeouts (datetime: 30s, system_info: 10min, user_info: 1hr)
- 30-120x speedup on cache hits
- Cache indicators in UI (💾 icon)

**Intent Analysis:**
- Classifies requests (Simple, Complex, Multi-step, Research, Control)
- Assesses complexity scores
- Plans multi-step execution
- Confidence scoring

**Learning System:**
- Tracks tool success rates
- Measures execution times
- Adapts to patterns
- Provides actionable suggestions

### Self-Correcting AI

The AI doesn't just execute - it learns from results:

```
User: "What's today's date?"

AI (initial): "Today is November 30, 2022"
[Executes current_date tool]
Tool Result: "Friday, February 06, 2026"
AI (corrected): "Apologies for the error. Today is actually February 6th, 2026."
```

### Smart Tool Selection

No hardcoded keywords! The AI reads the tool registry and decides:

```python
# AI sees this in system prompt:
Available Tools:
- current_date: Get the current date
- open_app: Open a desktop application
- web_search: Search the internet
```

Then intelligently chooses based on user intent!

## 🔧 Configuration

Configuration files in `config/`:
- `settings.json` - App settings
- `hardware.conf` - Hardware detection
- `active_project.json` - Current project

## 📝 Development

### Adding New Tools

1. Create tool function in `tools/system/` or `tools/web/`
2. Register in `tools/__init__.py`:

```python
"my_tool": {
    "module": "tools.system.my_module",
    "function": "my_function",
    "description": "What this tool does",
    "params": {"param1": "type"},
    "requires_commander": False
}
```

3. AI automatically discovers and uses it!

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Ollama for local AI models
- Electron for desktop framework
- React for UI framework
- Web Speech API for voice capabilities

## 📞 Support

Issues? Questions? Open an issue on GitHub!

---

**Built with 💙 by MrNova420**

*Making AI assistants truly intelligent, one tool at a time.* 🚀
