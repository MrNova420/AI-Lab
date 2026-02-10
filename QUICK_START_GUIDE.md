# 🚀 Quick Start Guide - Get Running in 5 Minutes!

Welcome to AI-Lab! This guide will get you up and running quickly.

---

## ⚡ Super Quick Start (30 Seconds!)

```bash
# 1. Clone
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab

# 2. Install (automated!)
./auto-install.sh

# 3. Run
./forge-app.sh
```

**That's it!** 🎉

---

## 📖 First Time Setup (5 Minutes)

### Step 1: Clone Repository (10 seconds)
```bash
git clone https://github.com/MrNova420/AI-Lab.git
cd AI-Lab
```

### Step 2: Run Auto-Installer (2 minutes)
```bash
./auto-install.sh
```

**What it does:**
- ✅ Checks your system (Python, Node.js, Git)
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up configuration
- ✅ Tests everything
- ✅ Shows next steps

### Step 3: Install Ollama (Optional, 2 minutes)

**Why?** To run AI models locally!

**Install:**
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows (WSL)
curl -fsSL https://ollama.com/install.sh | sh
```

**Get a Model:**
```bash
# Small & Fast (recommended for beginners)
ollama pull mistral

# Or for coding
ollama pull codellama

# Or tiny (1GB, works on anything!)
ollama pull tinyllama
```

### Step 4: Launch! (5 seconds)
```bash
./forge-app.sh
```

**Opens in your browser!** 🎊

---

## 🎯 Your First Conversation

### 1. Open the App
- Browser opens automatically at `http://localhost:5174`
- You'll see the chat interface

### 2. Try These Examples

**Simple Chat:**
```
You: "Hello! What can you help me with?"
AI: Introduces itself and capabilities
```

**Create Something:**
```
You: "Create a simple HTML website"
AI: Creates website files for you!
```

**Commander Mode:**
```
You: Click the ⚡ button to enable Commander Mode
You: "Check if Steam is installed"
AI: Checks and opens Steam or the website
```

**Research:**
```
You: "Search for Python tutorials"
AI: Finds resources and provides links
```

---

## 🎮 Quick Feature Tour

### Chat Mode 💬
- **What:** Standard text conversation
- **Use for:** General questions, code help, discussions
- **How:** Just type and press Enter!

### Voice Mode 🎤
- **What:** Voice commands (Web Speech API)
- **Use for:** Hands-free operation
- **How:** Click Voice tab, allow microphone

### Commander Mode ⚡
- **What:** Full system control
- **Use for:** Opening apps, system automation, file operations
- **How:** Click the ⚡ button in Chat

### Web Search Mode 🌐
- **What:** Internet research with verification
- **Use for:** Research, fact-checking, learning
- **How:** Built into responses automatically!

---

## 💡 Common Tasks

### Create a Project
```
You: "Create a Flask API for a blog"
AI: Generates complete API with files:
    - app.py
    - models.py
    - requirements.txt
    - README.md
```

### Open Applications
```
You: "Open Steam" (with Commander Mode)
AI: Checks if installed → Opens app or web
```

### Research Topics
```
You: "Research quantum computing"
AI: Multi-source search → Provides summary with citations
```

### Code Help
```
You: "Explain this code: [paste code]"
AI: Analyzes and explains clearly
```

### Debug Issues
```
You: "I'm getting this error: [paste error]"
AI: Identifies problem and suggests fixes
```

---

## ⚙️ Settings & Configuration

### Choose Your Model

**In the app:**
1. Go to Settings page
2. Select your Ollama model
3. Click "Set Active Model"

**Recommended Models:**

**Beginners:**
- `mistral` - Great balance (4.1GB)
- `codellama:7b` - For coding (3.8GB)

**Advanced:**
- `mixtral:8x7b` - Excellent quality (26GB)
- `llama2:70b` - Maximum quality (39GB)

**Tiny Devices:**
- `tinyllama` - Works anywhere (1GB)
- `qwen:1.8b` - Small & smart (1.1GB)

### Enable Commander Mode

**In Chat:**
1. Click the ⚡ Commander button
2. Confirm you want full system access
3. Now AI can control your system!

**Safety:** Commander Mode asks for confirmation on sensitive operations

---

## 🆘 Troubleshooting

### "Ollama not found"
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve
```

### "Python version too old"
```bash
# Check version
python3 --version

# Need 3.8+, recommended 3.12+
# Install from: https://www.python.org/downloads/
```

### "npm not found"
```bash
# Install Node.js
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS:
brew install node

# Windows: Download from nodejs.org
```

### "Tests failing"
```bash
# Run tests to see specific issue
python3 test_complete_system.py

# Check logs
cat logs/setup.log
```

### App won't start
```bash
# Try manual start
source venv/bin/activate
cd app
npm install
npm run dev
```

---

## 📚 Learn More

### Documentation
- **[Complete README](README.md)** - Full project info
- **[Installation Guide](INSTALLATION.md)** - Detailed setup
- **[Commander Mode Guide](COMMANDER_MODE_GUIDE.md)** - Features
- **[Local Model Guide](LOCAL_MODEL_GUIDE.md)** - Model selection

### Get Help
- **GitHub Issues:** Report bugs
- **GitHub Discussions:** Ask questions
- **Discord:** Coming soon!

---

## 🎯 Next Steps

### Beginner Path
1. ✅ Install and run (you're here!)
2. Try all modes (Chat, Voice, Commander)
3. Create your first project
4. Explore the dashboard
5. Check out the documentation

### Advanced Path
1. ✅ Install and run
2. Install multiple models
3. Try Commander Mode extensively
4. Build a real project
5. Contribute to the project

### Pro Path
1. ✅ Install and run
2. Read all documentation
3. Test with different models
4. Customize and extend
5. Submit pull requests

---

## 🎊 Tips & Tricks

### Be Specific
```
❌ "Make a website"
✅ "Create a portfolio website with HTML, CSS, and JavaScript"
```

### Use Commander Mode
```
✅ Enable ⚡ for system operations
✅ Let AI open apps, run commands
✅ Automate your workflows
```

### Explore Features
```
✅ Try Voice Mode
✅ Browse past sessions
✅ Export conversations
✅ Check the Dashboard analytics
```

### Ask for Help
```
You: "How do I use Commander Mode?"
AI: Explains clearly with examples
```

### Save Your Work
```
✅ Sessions auto-save every 5 seconds
✅ Export important conversations
✅ Name your sessions meaningfully
```

---

## 🌟 You're Ready!

**You now know how to:**
- ✅ Install AI-Lab
- ✅ Start the application
- ✅ Use all modes
- ✅ Create projects
- ✅ Get help when needed

**Start building amazing things!** 🚀

---

## ❓ FAQ

**Q: Is this free?**
A: Yes! 100% free and open source.

**Q: Does it work offline?**
A: Yes! Everything runs locally.

**Q: Can it access the internet?**
A: Only for web search (optional). AI runs locally.

**Q: What can I build?**
A: Anything! Websites, APIs, apps, games, scripts, etc.

**Q: Is my data private?**
A: Yes! Everything stays on your machine.

**Q: Can I use it commercially?**
A: Yes! MIT License allows commercial use.

**Q: Does it collect data?**
A: No! Zero telemetry, zero tracking.

**Q: Which model should I use?**
A: Start with Mistral 7B or CodeLlama 7B.

**Q: Can it replace my tools?**
A: It complements them! Use with VSCode, Git, etc.

**Q: Is it production-ready?**
A: Yes! v1.0.0 is fully tested and stable.

---

**Welcome to AI-Lab!** 💙

**Let's build something amazing together!** ✨🚀

---

**Need help? Just ask in the chat!** The AI is here to help you! 🤝
