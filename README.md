# 🧠 NovaForge AI Lab

**An intelligent, self-correcting AI assistant with voice control and system automation capabilities.**

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![Electron](https://img.shields.io/badge/Electron-Latest-47848F.svg)](https://www.electronjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

### 🧠 **Intelligent AI System**
- **Self-Correcting AI**: Uses real-world data to verify and correct responses
- **Smart Tool Selection**: AI analyzes intent and chooses appropriate tools (no hardcoded keywords!)
- **Tool Awareness**: Sees tool results before providing final answers
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
│   ├── runtime/          # Model runtime management
│   └── config.py         # Configuration management
├── scripts/              # Backend services
│   ├── api_server.py     # HTTP API server
│   ├── commander.py      # System control
│   └── smart_parser.py   # Tool call parser
└── tools/                # Tool registry
    ├── system/           # System tools
    └── web/              # Web tools
```

### How It Works

1. **User Input** → Voice or text
2. **AI Analysis** → Reads available tools and decides which to use
3. **Tool Declaration** → AI specifies tools: `<TOOLS>current_date</TOOLS>`
4. **Execution** → System runs tools and gets results
5. **Self-Correction** → AI sees results and provides accurate answer
6. **Display** → Clean output with tool results shown

## 🛠️ Available Tools

### Information Tools (Always Available)
- `current_date` - Get today's date
- `current_time` - Get current time
- `system_info` - System information
- `user_info` - User details

### Commander Tools (Requires ⚡ Mode)
- `open_app` - Open applications
- `close_app` - Close applications
- `screenshot` - Capture screen
- `mouse_move` - Move mouse cursor
- `mouse_click` - Click mouse
- `keyboard_type` - Type text
- `keyboard_press` - Press keys

### Web Tools (Requires 🌐 Mode)
- `web_search` - Search the internet
- `verify_info` - Fact-check claims
- `open_url` - Open websites

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
