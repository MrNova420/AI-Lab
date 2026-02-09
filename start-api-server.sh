#!/bin/bash
# Start API Server with proper environment

cd "$(dirname "$0")"

echo "🚀 Starting AI-Lab API Server..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Using system Python."
    echo "💡 Run ./setup.sh to create one."
fi

# Start the API server
python3 scripts/api_server.py
