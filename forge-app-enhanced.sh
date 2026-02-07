#!/bin/bash
# Enhanced logging wrapper for forge-app.sh

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Symbols
CHECK="✓"
CROSS="✗"
ARROW="➜"
STAR="★"
GEAR="⚙"

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                     🚀 NovaForge AI System Launcher 🚀${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# System info
echo -e "${BLUE}${GEAR} SYSTEM INFORMATION:${NC}"
echo -e "   ${ARROW} Hostname: ${WHITE}$(hostname)${NC}"
echo -e "   ${ARROW} User: ${WHITE}$(whoami)${NC}"
echo -e "   ${ARROW} Date: ${WHITE}$(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "   ${ARROW} Working Directory: ${WHITE}$(pwd)${NC}"
echo -e "   ${ARROW} Python Version: ${WHITE}$(python3 --version 2>&1)${NC}"
echo -e "   ${ARROW} Node Version: ${WHITE}$(node --version 2>&1)${NC}"
echo ""

# Check dependencies
echo -e "${BLUE}${GEAR} CHECKING DEPENDENCIES:${NC}"

check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "   ${GREEN}${CHECK}${NC} $2: ${GREEN}Found${NC}"
        return 0
    else
        echo -e "   ${RED}${CROSS}${NC} $2: ${RED}Not found${NC}"
        return 1
    fi
}

check_command python3 "Python 3"
check_command node "Node.js"
check_command npm "NPM"
check_command git "Git"

echo ""

# Check virtual environment
echo -e "${BLUE}${GEAR} VIRTUAL ENVIRONMENT:${NC}"
if [ -d "venv" ]; then
    echo -e "   ${GREEN}${CHECK}${NC} Virtual environment: ${GREEN}Found${NC}"
    echo -e "   ${ARROW} Location: ${WHITE}$(pwd)/venv${NC}"
    
    # Activate and check packages
    source venv/bin/activate 2>/dev/null
    echo -e "   ${GREEN}${CHECK}${NC} Environment: ${GREEN}Activated${NC}"
    
    # Check key Python packages
    echo ""
    echo -e "${BLUE}${GEAR} PYTHON PACKAGES:${NC}"
    for pkg in aiohttp beautifulsoup4 requests psutil gputil ollama; do
        if python3 -c "import $pkg" 2>/dev/null; then
            version=$(python3 -c "import $pkg; print(getattr($pkg, '__version__', 'unknown'))" 2>/dev/null)
            echo -e "   ${GREEN}${CHECK}${NC} $pkg: ${GREEN}$version${NC}"
        else
            echo -e "   ${YELLOW}⚠${NC} $pkg: ${YELLOW}Not installed${NC}"
        fi
    done
else
    echo -e "   ${RED}${CROSS}${NC} Virtual environment: ${RED}Not found${NC}"
fi

echo ""

# Check API server
echo -e "${BLUE}${GEAR} CHECKING API SERVER:${NC}"
API_PID=$(pgrep -f "scripts/api_server.py" | head -1)
if [ ! -z "$API_PID" ]; then
    echo -e "   ${YELLOW}⚠${NC} API server already running: ${YELLOW}PID $API_PID${NC}"
    echo -e "   ${ARROW} Will be restarted automatically"
else
    echo -e "   ${GREEN}${CHECK}${NC} No existing API server (ready to start)"
fi

echo ""

# Check app directory
echo -e "${BLUE}${GEAR} APPLICATION FILES:${NC}"
if [ -d "app" ]; then
    echo -e "   ${GREEN}${CHECK}${NC} App directory: ${GREEN}Found${NC}"
    if [ -f "app/package.json" ]; then
        echo -e "   ${GREEN}${CHECK}${NC} package.json: ${GREEN}Found${NC}"
        APP_NAME=$(cat app/package.json | grep '"name"' | head -1 | cut -d '"' -f 4)
        APP_VERSION=$(cat app/package.json | grep '"version"' | head -1 | cut -d '"' -f 4)
        echo -e "   ${ARROW} App: ${WHITE}$APP_NAME v$APP_VERSION${NC}"
    fi
    if [ -d "app/node_modules" ]; then
        echo -e "   ${GREEN}${CHECK}${NC} node_modules: ${GREEN}Found${NC}"
    else
        echo -e "   ${YELLOW}⚠${NC} node_modules: ${YELLOW}Not found (run npm install)${NC}"
    fi
else
    echo -e "   ${RED}${CROSS}${NC} App directory: ${RED}Not found${NC}"
fi

echo ""

# Check ports
echo -e "${BLUE}${GEAR} PORT AVAILABILITY:${NC}"
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -Pi :$1 -sTCP:LISTEN -t)
        PROC=$(ps -p $PID -o comm= 2>/dev/null || echo "unknown")
        echo -e "   ${YELLOW}⚠${NC} Port $1: ${YELLOW}In use by $PROC (PID $PID)${NC}"
        return 1
    else
        echo -e "   ${GREEN}${CHECK}${NC} Port $1: ${GREEN}Available${NC}"
        return 0
    fi
}

check_port 5000  # API server
check_port 5173  # Vite dev server

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    ${STAR} ALL CHECKS COMPLETE ${STAR}${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${WHITE}${ARROW} Starting NovaForge in 3 seconds...${NC}"
sleep 1
echo -e "${WHITE}${ARROW} 2...${NC}"
sleep 1
echo -e "${WHITE}${ARROW} 1...${NC}"
sleep 1

echo ""
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                        🎬 LAUNCHING APPLICATION 🎬${NC}"
echo -e "${PURPLE}════════════════════════════════════════════════════════════════════════${NC}"
echo ""

# Run the actual app
./forge-app.sh
