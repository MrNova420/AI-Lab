#!/bin/bash
# NovaForge Desktop App Launcher

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/app"

echo "🚀 Starting NovaForge Desktop App..."

# Check if node_modules exists
if [ ! -d "$APP_DIR/node_modules" ]; then
    echo "📦 Installing dependencies..."
    cd "$APP_DIR" && npm install
fi

# Start API server in background
echo "🔧 Starting API server..."
cd "$SCRIPT_DIR"
source venv/bin/activate
nohup python scripts/api_server.py > logs/api_server.log 2>&1 &
API_PID=$!
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

# Start the app in development mode
cd "$APP_DIR"
echo "✅ Launching app..."
echo ""
npm run electron:dev

# Cleanup on exit
trap "kill $API_PID 2>/dev/null" EXIT
