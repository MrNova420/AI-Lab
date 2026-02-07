#!/bin/bash
echo "🧹 AI-Lab Quick Cleanup"
echo ""
echo "Finding processes..."
echo ""

# API servers
api_pids=$(ps aux | grep "python.*api_server" | grep -v grep | awk '{print $2}')
if [ ! -z "$api_pids" ]; then
    echo "API servers found:"
    for pid in $api_pids; do
        echo "  kill -9 $pid"
    done
fi

# Electron
electron_pids=$(ps aux | grep "electron" | grep -v grep | awk '{print $2}')
if [ ! -z "$electron_pids" ]; then
    echo "Electron processes found:"
    for pid in $electron_pids; do
        echo "  kill -9 $pid"
    done
fi

# Stuck Ollama
ollama_pids=$(ps aux | grep "ollama runner" | grep -v grep | awk '{print $2}')
if [ ! -z "$ollama_pids" ]; then
    echo "⚠️  STUCK OLLAMA RUNNERS:"
    ps aux | grep "ollama runner" | grep -v grep | awk '{print "  sudo kill -9", $2, "(CPU:", $3"%)"}'
fi

echo ""
echo "Copy/paste the kill commands above to clean up!"
