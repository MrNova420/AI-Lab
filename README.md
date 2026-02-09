# 🧠 NovaForge AI Lab

**An intelligent, self-correcting AI assistant with voice control and system automation capabilities.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Electron](https://img.shields.io/badge/Electron-Latest-47848F.svg)](https://www.electronjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎉 Recent Updates (February 7, 2026)

### ✅ Major Overhaul Complete - Tool Execution System Fixed!

The core AI tool execution system has been completely rewritten and is now **fully functional**:

**What Changed:**
- ✨ **NEW**: Intelligent tool executor that dynamically loads and runs tools
- ✨ **NEW**: AI now analyzes requests and chooses tools intelligently (no hardcoded keywords!)
- ✨ **NEW**: Complete tool modules for system control (apps, screenshots, mouse, keyboard)
- 🔧 **FIXED**: Commander Mode now uses AI intelligence instead of keyword matching
- 🔧 **FIXED**: Web Search Mode properly integrated with search tools
- 🔧 **FIXED**: API handler completely rewritten to support tool execution pipeline
- 📚 **NEW**: Comprehensive documentation and testing

**Key Features:**
- 🧠 AI reads tool registry and decides which tools to use
- 🔐 Permission system prevents unsafe tool execution
- 🛠️ All tools in the registry are now properly functional
- 🧪 Full test suite with integration tests
- 📖 Complete architecture documentation

**Read More:**
- [Tool Execution System Architecture](docs/TOOL_EXECUTION_SYSTEM.md)
- [Complete Project Analysis & Fixes](docs/PROJECT_FIXES_SUMMARY.md)
- [Development Roadmap](docs/ROADMAP.md)

---

## ✨ Features

### 🧠 **Intelligent AI System**
- **Self-Correcting AI**: Uses real-world data to verify and correct responses
- **Smart Tool Selection**: AI analyzes intent and chooses appropriate tools (no hardcoded keywords!)
- **Tool Awareness**: Sees tool results before providing final answers
- **Reasoning & Learning Layer**: Context-aware system that learns from interactions
- **Smart Caching**: 30-120x speedup with intelligent cache management
- **Session Persistence**: Maintains context across restarts
- **Dynamic Tool Registry**: Extensible architecture for adding new capabilities

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
- Modern, responsive UI
- Voice and text chat interfaces
- Model management
- Project system

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
├── tools/                # Tool registry (21 tools)
│   ├── __init__.py       # Dynamic tool registry
│   ├── system/           # System tools (datetime, apps, screenshots)
│   ├── input/            # ✨ NEW! Mouse & keyboard control
│   └── web/              # Web tools (search, verify, scrape)
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

**21 tools across 3 categories** - See [CURRENT_TOOLS.md](CURRENT_TOOLS.md) for full documentation.

### Information Tools (Always Available)
- `datetime` - Get current date/time with timezone
- `system_info` - Real system information (OS, CPU, RAM, kernel)
- `user_info` - User details (username, home directory, shell)
- `check_app` - Check if application is installed

### Commander Tools (Requires ⚡ Mode)
- `open_app` / `close_app` / `switch_app` - Application management
- `screenshot` - Capture screen
- `mouse_move` / `mouse_click` - Mouse control
- `keyboard_type` / `keyboard_press` / `keyboard_combo` - Keyboard automation
- `analyze_system` - System diagnostics

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
