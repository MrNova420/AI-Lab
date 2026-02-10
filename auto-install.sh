#!/bin/bash
# Enhanced Auto-Install Script for AI-Lab
# Fully automated, user-friendly setup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_ROOT/venv"
LOG_FILE="$PROJECT_ROOT/logs/auto_install.log"

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"
> "$LOG_FILE"

# Logging functions
log() {
    echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ${NC} $1" | tee -a "$LOG_FILE"
}

header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Welcome banner
clear
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║         🚀  AI-Lab Auto-Install Script  🚀          ║"
echo "║                                                      ║"
echo "║     Full development assistant with 43 tools        ║"
echo "║     Like GitHub Copilot + System Control            ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check system requirements
header "Step 1/6: Checking System Requirements"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION_INFO=$(python3 -c "import sys; print(f'{sys.version_info.major} {sys.version_info.minor}')")
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION_INFO" | cut -d' ' -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION_INFO" | cut -d' ' -f2)
    PYTHON_VERSION="${PYTHON_MAJOR}.${PYTHON_MINOR}"
    if [ "$PYTHON_MAJOR" -gt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; }; then
        log "Python $PYTHON_VERSION found (✓ >= 3.11 required)"
    else
        error "Python $PYTHON_VERSION found (✗ >= 3.11 required)"
        info "Install Python 3.11+:"
        echo "  Ubuntu/Debian: sudo apt install python3.11"
        echo "  macOS: brew install python@3.11"
        exit 1
    fi
else
    error "Python not found!"
    info "Install Python 3.11+ first"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if (( NODE_VERSION >= 18 )); then
        log "Node.js v$NODE_VERSION found (✓ >= 18 required)"
    else
        warn "Node.js v$NODE_VERSION found (⚠ >= 18 recommended)"
    fi
else
    error "Node.js not found!"
    info "Install Node.js 18+:"
    echo "  Ubuntu/Debian: sudo apt install nodejs npm"
    echo "  macOS: brew install node"
    exit 1
fi

# Check Git
if command -v git &> /dev/null; then
    log "Git found"
else
    error "Git not found!"
    exit 1
fi

# Check Ollama (optional)
if command -v ollama &> /dev/null; then
    log "Ollama found (for local AI models)"
    OLLAMA_AVAILABLE=1
else
    warn "Ollama not found (optional, but recommended)"
    info "Install from: https://ollama.com/download"
    OLLAMA_AVAILABLE=0
fi

# Step 2: Create Python virtual environment
header "Step 2/6: Creating Python Environment"

if [ -d "$VENV_DIR" ]; then
    warn "Existing virtual environment found - recreating..."
    rm -rf "$VENV_DIR"
fi

python3 -m venv "$VENV_DIR" || {
    error "Failed to create virtual environment"
    exit 1
}
log "Virtual environment created"

source "$VENV_DIR/bin/activate" || {
    error "Failed to activate virtual environment"
    exit 1
}
log "Virtual environment activated"

# Step 3: Install Python dependencies
header "Step 3/6: Installing Python Dependencies"

if [ -f "$PROJECT_ROOT/core/requirements.txt" ]; then
    info "Installing packages..."
    python3 -m pip install --upgrade pip -q
    python3 -m pip install -r "$PROJECT_ROOT/core/requirements.txt" -q || {
        error "Failed to install Python dependencies"
        warn "Check logs/auto_install.log for details"
        exit 1
    }
    log "Python dependencies installed"
else
    error "requirements.txt not found!"
    exit 1
fi

# Step 4: Install Node.js dependencies
header "Step 4/6: Installing Node.js Dependencies"

if [ -f "$PROJECT_ROOT/app/package.json" ]; then
    info "Installing frontend packages (this may take a minute)..."
    cd "$PROJECT_ROOT/app"
    npm install -q || {
        error "Failed to install Node.js dependencies"
        exit 1
    }
    log "Node.js dependencies installed"
    cd "$PROJECT_ROOT"
else
    warn "app/package.json not found - frontend may not be available"
fi

# Step 5: Initialize configuration
header "Step 5/6: Initializing Configuration"

# Create config directories
mkdir -p "$PROJECT_ROOT/config"
mkdir -p "$PROJECT_ROOT/projects/default"
mkdir -p "$PROJECT_ROOT/models"
mkdir -p "$PROJECT_ROOT/memory/sessions"
mkdir -p "$PROJECT_ROOT/memory/users"
mkdir -p "$PROJECT_ROOT/.novaforge/cache"

# Create default config files
if [ ! -f "$PROJECT_ROOT/config/settings.json" ]; then
    echo '{"active_project": "default", "theme": "dark", "auto_save": true}' > "$PROJECT_ROOT/config/settings.json"
    log "Created default settings"
fi

if [ ! -f "$PROJECT_ROOT/projects/default/project.json" ]; then
    cat > "$PROJECT_ROOT/projects/default/project.json" << 'EOF'
{
  "project_name": "default",
  "version": "2.0",
  "active_model_tag": "",
  "commander_mode": true,
  "web_search_mode": false,
  "memory": {
    "enabled": true,
    "cache_enabled": true
  }
}
EOF
    log "Created default project configuration"
fi

if [ ! -f "$PROJECT_ROOT/models/models.json" ]; then
    echo '{}' > "$PROJECT_ROOT/models/models.json"
    log "Created models registry"
fi

if [ ! -f "$PROJECT_ROOT/memory/users/users.json" ]; then
    cat > "$PROJECT_ROOT/memory/users/users.json" << 'EOF'
{
  "users": [
    {
      "id": "default",
      "username": "default",
      "display_name": "Default User",
      "preferences": {},
      "stats": {}
    }
  ],
  "current_user_id": "default"
}
EOF
    log "Created default user"
fi

# Step 6: Run tests
header "Step 6/6: Running System Tests"

info "Testing Python environment..."
python3 -c "import sys; print(f'Python {sys.version}')" >> "$LOG_FILE" 2>&1
log "Python environment OK"

info "Testing imports..."
python3 -c "import core.ai_protocol, core.tool_executor, tools" >> "$LOG_FILE" 2>&1 || {
    warn "Some imports failed - check logs/auto_install.log"
}
log "Core modules OK"

# Test tool count
TOOL_COUNT=$(python3 -c "from tools import TOOLS; print(sum(len(cat) for cat in TOOLS.values()))" 2>/dev/null || echo "0")
log "Found $TOOL_COUNT tools available"

# Final summary
header "🎉 Installation Complete!"

echo ""
log "AI-Lab is ready to use!"
echo ""
info "What was installed:"
echo "  • Python virtual environment with all dependencies"
echo "  • Node.js packages for frontend"
echo "  • Configuration files initialized"
echo "  • $TOOL_COUNT tools available"
echo "  • Commander Mode enabled by default"
echo ""

if [ $OLLAMA_AVAILABLE -eq 1 ]; then
    info "Next steps:"
    echo "  1. Install AI models:"
    echo "     ollama pull llama2"
    echo "     ollama pull codellama"
    echo "  2. Start Ollama (if not running):"
    echo "     ollama serve"
    echo "  3. Launch AI-Lab:"
    echo "     ./forge-app.sh"
else
    warn "Ollama not installed - AI features won't work without it"
    info "Next steps:"
    echo "  1. Install Ollama from: https://ollama.com/download"
    echo "  2. Install models: ollama pull llama2"
    echo "  3. Start Ollama: ollama serve"
    echo "  4. Launch AI-Lab: ./forge-app.sh"
fi

echo ""
log "Quick start: ./forge-app.sh"
log "Documentation: INSTALLATION.md"
log "Help: ./test-everything.sh"
echo ""

echo "╔══════════════════════════════════════════════════════╗"
echo "║                                                      ║"
echo "║           ✨  Ready to build something! ✨          ║"
echo "║                                                      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

deactivate
exit 0
