#!/bin/bash
# AI-Lab Desktop App Launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"

echo "🚀 Starting AI-Lab..."

# Store all child PIDs for cleanup
CLEANUP_PIDS=()

# Cleanup function - RUNS ON EXIT, CTRL+C, OR WINDOW CLOSE
cleanup() {
    echo ""
    echo "🛑 Shutting down AI-Lab..."
    
    # Kill API server
    if [ ! -z "$API_PID" ]; then
        echo "   Stopping API server (PID: $API_PID)..."
        kill -9 $API_PID 2>/dev/null || true
    fi
    
    # Kill all tracked child processes
    for pid in "${CLEANUP_PIDS[@]}"; do
        kill -9 $pid 2>/dev/null || true
    done
    
    # Kill any remaining processes from this session
    # This ensures Electron, Vite, npm all get cleaned up
    if [ ! -z "$$" ]; then
        pkill -9 -P $$ 2>/dev/null || true
    fi
    
    # Force kill any remaining project processes
    pkill -9 -f "ai-forge.*api_server" 2>/dev/null || true
    pkill -9 -f "ai-forge.*electron" 2>/dev/null || true
    pkill -9 -f "ai-forge.*vite" 2>/dev/null || true
    
    echo "✅ Cleanup complete - all processes stopped"
    exit 0
}

# Set trap for ALL exit scenarios
trap cleanup EXIT INT TERM HUP

# Check if node_modules exists
if [ ! -d "$APP_DIR/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd "$APP_DIR" && npm install
fi

# Start API server in background
echo "🔧 Starting API server..."
cd "$SCRIPT_DIR"
source venv/bin/activate
python scripts/api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
CLEANUP_PIDS+=($API_PID)
echo "✅ API server started (PID: $API_PID)"
sleep 2

# Auto-open browser window after a delay
(
  sleep 5
  echo ""
  echo "🌐 Auto-opening browser window..."
  
  # Try different methods to open browser
  if command -v cmd.exe &> /dev/null; then
    # WSL - use Windows command
    cmd.exe /c start http://localhost:5173 2>/dev/null &
  elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:5173 &
  elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:5173 &
  fi
  
  echo "✅ Browser opened at http://localhost:5173"
) &
CLEANUP_PIDS+=($!)

# Start the app in development mode
cd "$APP_DIR"
echo "✅ Launching app..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   Press Ctrl+C to stop (all processes will clean up)"
echo "   Or close this window to fully shut down"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
npm run electron:dev

# Note: cleanup() will automatically run when npm exits
