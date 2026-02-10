# 🚀 AI-Lab Installation Guide

**Simple, Fast, Automated Setup**

Get AI-Lab running in under 5 minutes!

---

## ⚡ Quick Start (Recommended)

### One-Command Install:

```bash
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
./setup.sh && ./forge-app.sh
```

That's it! The app will:
1. ✅ Check system requirements
2. ✅ Install all dependencies  
3. ✅ Set up configuration
4. ✅ Launch the application
5. ✅ Open browser automatically

---

## 📋 System Requirements

### Required:
- **Python** 3.11 or newer
- **Node.js** 18 or newer
- **Git** (for cloning)
- **4GB RAM minimum** (8GB+ recommended)

### Optional:
- **Ollama** (for local AI models) - [Download](https://ollama.com/download)
- **CUDA/ROCm** (for GPU acceleration)

---

## 🖥️ Platform-Specific Instructions

### 🐧 Linux (Ubuntu/Debian)

```bash
# Install prerequisites
sudo apt update
sudo apt install -y python3.11 python3.11-venv nodejs npm git wget

# Install Ollama (optional but recommended)
curl -fsSL https://ollama.com/install.sh | sh

# Clone and run
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
./setup.sh
./forge-app.sh
```

### 🪟 Windows (WSL Recommended)

#### Option 1: WSL2 (Recommended)

```powershell
# In PowerShell (Admin):
wsl --install Ubuntu-22.04
wsl --set-version Ubuntu-22.04 2

# In WSL Ubuntu:
sudo apt update && sudo apt install -y python3.11 nodejs npm git
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
./setup.sh
./forge-app.sh
```

#### Option 2: Native Windows

```powershell
# Install prerequisites:
# - Python 3.11+ from python.org
# - Node.js 18+ from nodejs.org
# - Git from git-scm.com

# Then in PowerShell:
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
bash setup.sh  # Or python setup.py if created
```

### 🍎 macOS

```bash
# Install Homebrew if needed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install prerequisites
brew install python@3.11 node git wget

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Clone and run
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
./setup.sh
./forge-app.sh
```

---

## 📦 What Gets Installed

### Python Dependencies:
- `requests` - HTTP client
- `aiohttp` - Async HTTP
- `beautifulsoup4` - Web scraping
- `prompt_toolkit` - Terminal UI
- `filelock` - Safe file operations
- `psutil` - System monitoring
- `pytest` - Testing framework
- `gitpython` - Git integration

### Node.js Dependencies:
- `electron` - Desktop framework
- `react` - UI framework
- `vite` - Build tool
- And other required packages

### Project Structure:
```
AI-Lab/
├── venv/           # Python virtual environment
├── node_modules/   # Node.js packages (in app/)
├── config/         # Configuration files
├── projects/       # Project workspaces
├── models/         # AI model registry
├── memory/         # Session and user data
├── logs/           # Application logs
└── .novaforge/     # Cache directory (in home)
```

---

## 🎮 Running AI-Lab

### Desktop App (Recommended):
```bash
./forge-app.sh
```
Opens at `http://localhost:5173` automatically

### CLI Mode:
```bash
./forge.sh
```
Interactive terminal menu

### API Server Only:
```bash
./start-api-server.sh
```
Runs on `http://localhost:5001`

---

## ⚙️ Configuration

### First-Time Setup:

1. **Install Ollama models** (if using local AI):
   ```bash
   ollama pull llama2
   ollama pull codellama
   ollama pull mistral
   ```

2. **Configure AI-Lab**:
   - Open the app
   - Go to **Models** page
   - Select your model
   - Enable **Commander Mode** for full features

3. **Test the system**:
   ```bash
   ./test-everything.sh
   ```

---

## 🔧 Troubleshooting

### Issue: "Python 3.11 not found"
```bash
# Ubuntu/Debian:
sudo apt install python3.11 python3.11-venv

# macOS:
brew install python@3.11

# Check version:
python3 --version
```

### Issue: "npm command not found"
```bash
# Ubuntu/Debian:
sudo apt install nodejs npm

# macOS:
brew install node

# Check version:
node --version  # Should be 18+
```

### Issue: "Ollama not running"
```bash
# Start Ollama service:
ollama serve

# Or check if running:
curl http://localhost:11434/api/tags

# Install Ollama if missing:
curl -fsSL https://ollama.com/install.sh | sh
```

### Issue: "Port 5173 already in use"
```bash
# Find and kill the process:
lsof -ti:5173 | xargs kill -9

# Or use a different port:
PORT=3000 ./forge-app.sh
```

### Issue: "Dependencies fail to install"
```bash
# Clean and reinstall:
rm -rf venv/ app/node_modules/
./setup.sh
cd app && npm install
```

### Issue: "Browser doesn't open automatically"
Manually open: `http://localhost:5173`

---

## 🚀 Advanced Setup

### Using Custom Python:
```bash
export PYTHON=/path/to/python3.11
./setup.sh
```

### Using Custom Ollama:
```bash
export OLLAMA_HOST=http://remote-server:11434
./forge-app.sh
```

### Development Mode:
```bash
# Backend development:
source venv/bin/activate
python scripts/api_server.py

# Frontend development:
cd app
npm run dev
```

### GPU Acceleration:
```bash
# NVIDIA CUDA:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# AMD ROCm:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.6
```

---

## 📊 System Check

Run comprehensive system test:
```bash
./test-everything.sh
```

Check specific components:
```bash
# Test Python environment:
source venv/bin/activate && python -c "import sys; print(sys.version)"

# Test Ollama connection:
curl http://localhost:11434/api/tags

# Test API server:
curl http://localhost:5001/api/models

# Test frontend build:
cd app && npm run build
```

---

## 🆘 Getting Help

### Documentation:
- **Commander Mode Guide**: `COMMANDER_MODE_GUIDE.md`
- **Tool Documentation**: `CURRENT_TOOLS.md`
- **Development Guide**: `docs/DEVELOPMENT.md`
- **API Reference**: `docs/API.md`

### Common Issues:
- Check `logs/setup.log` for setup errors
- Check `logs/api_server.log` for runtime errors
- Run `./test-everything.sh` for diagnostics

### Support:
- GitHub Issues: https://github.com/MrNova420/AI-Lab/issues
- Discussions: https://github.com/MrNova420/AI-Lab/discussions

---

## 🎯 Quick Tips

1. **Enable Commander Mode** for full development features
2. **Install multiple Ollama models** for different tasks
3. **Use Git integration** for version control workflows
4. **Check Dashboard** for system stats and tool usage
5. **Browse Sessions** to review past conversations

---

## ✅ Verification Checklist

After installation, verify:

- [ ] `./setup.sh` completed successfully
- [ ] `source venv/bin/activate` works
- [ ] `python --version` shows 3.11+
- [ ] `node --version` shows 18+
- [ ] `ollama list` shows installed models
- [ ] `./forge-app.sh` launches the app
- [ ] Browser opens to `http://localhost:5173`
- [ ] API server responds at `http://localhost:5001`
- [ ] Commander Mode button (⚡) visible in UI
- [ ] Can send messages and get responses

---

## 🎉 You're Ready!

AI-Lab is now fully installed and ready to use!

**Next Steps:**
1. Open the app with `./forge-app.sh`
2. Enable **Commander Mode** (⚡ button)
3. Try: "Analyze this project"
4. Explore the 43 available tools
5. Build something amazing! 🚀

---

**Need help?** Check the troubleshooting section or open an issue on GitHub.

**Happy coding!** 💙
