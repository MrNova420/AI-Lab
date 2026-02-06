#!/bin/bash

# Start NovaForge in browser mode (with API server)

cd "$(dirname "$0")"

echo "🚀 Starting NovaForge (Browser Mode)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Start API server in background
echo "📡 Starting API server..."
venv/bin/python scripts/api_server.py 5174 > logs/api_server.log 2>&1 &
API_PID=$!
echo "✅ API server started (PID: $API_PID)"

# Auto-open 1 browser window after a delay
(
  sleep 5
  echo ""
  echo "🌐 Auto-opening browser window..."
  
  # Try different methods
  if command -v cmd.exe &> /dev/null; then
    # WSL
    cmd.exe /c start http://localhost:5173 2>/dev/null &
  elif command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:5173 &
  elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:5173 &
  fi
  
  echo "✅ Browser opened!"
) &

# Start Vite dev server
echo "🌐 Starting Vite dev server..."
cd app
npm run dev &
VITE_PID=$!

echo ""
echo "✅ NovaForge is ready!"
echo ""
echo "🌐 Access at: http://localhost:5173"
echo "📡 API server: http://localhost:5174"
echo ""
echo "Press Ctrl+C to stop all services"

# Handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $API_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
