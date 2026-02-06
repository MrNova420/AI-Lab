# 🚀 NovaForge Desktop App

Modern desktop application for NovaForge AI Lab with native audio support - **NO WSL audio bridge issues!**

## ✨ Features

### 🎯 Core Functionality
- **💬 Chat** - Stream text conversations with your AI models
- **🎤 Voice Assistant** - Hands-free AI using native Web Audio API
- **📦 Model Management** - Download, select, and remove Ollama models
- **📊 Dashboard** - System status and quick stats
- **⚙️ Settings** - Configure your AI environment

### 🔥 Key Advantages
- ✅ **Native Audio** - Uses browser MediaRecorder API (no WSL audio configuration!)
- ✅ **Bluetooth Support** - Auto-detects all system microphones including Bluetooth
- ✅ **Real-time Streaming** - See AI responses token-by-token as they generate
- ✅ **Auto Model Sync** - Automatically detects ALL your Ollama models
- ✅ **Modern UI** - Dark theme, smooth animations, intuitive navigation

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for Electron)
- Python 3.10+ with virtualenv
- Ollama installed and running

### Installation

1. **Install Node dependencies** (first time only):
```bash
cd ai-forge/app
npm install
```

2. **Launch the app**:
```bash
cd ai-forge
./forge-app.sh
```

The app will:
- Auto-install dependencies if needed
- Start Vite dev server (port 5173)
- Launch Electron window
- Auto-sync your Ollama models

## 📖 Usage Guide

### Chat Page
1. Navigate to **Chat** from the sidebar
2. Type your message in the input box
3. Press Enter or click **Send**
4. Watch AI response stream in real-time!
5. Click **Clear Chat** to start fresh

**Tips:**
- Use Shift+Enter for multi-line messages
- Last 10 messages kept for context
- Responses support markdown formatting

### Voice Assistant
1. Navigate to **Voice** from the sidebar
2. Select your microphone from dropdown
3. Click the big **microphone button** to record
4. Speak your message (auto-stops after 8 seconds)
5. AI transcribes, responds, and speaks back!

**Features:**
- 🎙️ Native browser audio recording (works in WSL!)
- 🔊 Text-to-Speech using Web Speech API
- 📝 Full conversation history
- 🎧 Auto-detects all microphones (USB, Bluetooth, built-in)

**Browser Permissions:**
- Grant microphone access when prompted
- Check browser settings if no mics detected

### Models Page
1. Navigate to **Models** from the sidebar
2. See all your downloaded Ollama models
3. Click **🔄 Sync** to refresh from Ollama
4. Click **Download Model** to get new ones

**Quick Download:**
- Select from popular models (Llama, Mistral, Phi, etc.)
- Or enter custom tag: `mistral:7b-instruct`
- Download happens in background

**Model Management:**
- **Select** - Set as active model for chat/voice
- **Remove** - Delete from Ollama (careful!)
- Active model shown with blue border

### Dashboard
- View active project and model
- See total models downloaded
- Quick status overview
- Getting started guide

## 🛠️ Development

### Project Structure
```
ai-forge/app/
├── main/           # Electron main process
│   └── index.js    # IPC handlers, Python bridge
├── preload/        # Secure IPC bridge
│   └── index.js    # Exposed APIs
├── renderer/       # React frontend
│   └── src/
│       ├── App.jsx       # Router & navigation
│       ├── pages/        # Page components
│       ├── components/   # Reusable components
│       └── hooks/        # Custom React hooks
├── package.json    # Dependencies
└── vite.config.js  # Vite configuration
```

### Development Mode
```bash
npm run electron:dev
```

This runs:
- Vite dev server with HMR (hot reload)
- Electron in development mode
- DevTools automatically opened

### Building for Production
```bash
npm run build        # Build React app
npm run electron:build  # Package Electron app
```

### Adding New Features

#### 1. Add IPC Handler (main/index.js)
```javascript
ipcMain.handle('my-feature:action', async (event, arg) => {
  // Call Python backend via spawn
  return result;
});
```

#### 2. Expose API (preload/index.js)
```javascript
myFeature: {
  action: (arg) => ipcRenderer.invoke('my-feature:action', arg)
}
```

#### 3. Use in React (pages/MyPage.jsx)
```javascript
const result = await window.electron.myFeature.action(arg);
```

## 🐛 Troubleshooting

### App won't start
```bash
# Clean install
cd app
rm -rf node_modules package-lock.json
npm install
```

### Python bridge errors
```bash
# Ensure venv is activated
cd ..
source venv/bin/activate
pip install -r requirements.txt
```

### Microphone not detected (Voice page)
1. Check browser permissions (usually top bar)
2. Try different browser (Chrome/Edge recommended)
3. Test mic in browser settings first
4. Bluetooth: Ensure device is connected AND set as input device

### Models not syncing
1. Check Ollama is running: `ollama list`
2. Click **🔄 Sync** button manually
3. Check console for errors (DevTools)

### Chat/Voice responses failing
1. Verify active model is selected (Models page)
2. Check Ollama is running: `ollama list`
3. Test in terminal: `ollama run <model>`

## 🎯 Tips & Tricks

### Performance
- **First load slow?** Models are syncing - be patient!
- **Streaming stuttering?** Close other Electron apps
- **High CPU?** Check Ollama model size - try smaller model

### Best Models for Voice
- **Fastest:** `llama3.2:1b` (1GB)
- **Balanced:** `llama3.2:3b` (2GB)  
- **Best quality:** `mistral:7b` (4GB)

### Keyboard Shortcuts
- **Chat:** Enter = send, Shift+Enter = new line
- **DevTools:** Ctrl+Shift+I (or Cmd+Opt+I on Mac)

### Voice Tips
- Speak clearly, not too fast
- Quiet environment = better transcription
- Use headphones to prevent echo
- Hands-free mode coming soon!

## 🔒 Security Notes

- **contextIsolation:** Enabled (renderer isolated from Node.js)
- **nodeIntegration:** Disabled (no direct Node access from renderer)
- **Preload script:** Only specific APIs exposed
- **Python calls:** Sandboxed via spawn, no shell injection

## 🚀 Roadmap

### Phase 2 (Current)
- [x] Core chat functionality
- [x] Voice with native audio
- [x] Model management
- [ ] Projects page
- [ ] Settings page

### Phase 3 (Next)
- [ ] Conversation history persistence
- [ ] Export conversations
- [ ] Model download progress
- [ ] Voice wake word detection
- [ ] System tray integration

### Phase 4 (Future)
- [ ] Multi-modal (vision models)
- [ ] Agent tools integration
- [ ] Training/fine-tuning UI
- [ ] Cloud sync
- [ ] Mobile companion app

## 📝 Notes

### WSL Users
The desktop app **bypasses WSL audio issues** entirely by using browser APIs! The terminal voice assistant may still have issues due to PulseAudio bridge, but the desktop app works perfectly.

### Windows Users
Full native support - no WSL needed!

### macOS/Linux Users
Native support with system audio.

## 🤝 Contributing

See main project README for contribution guidelines.

## 📄 License

MIT - See LICENSE file

---

**Made with ❤️ by the NovaForge team**

Need help? Check the [main docs](../docs/) or open an issue!
