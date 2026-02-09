#!/bin/bash
# Start API Server with proper environment

cd "$(dirname "$0")"

echo "🚀 Starting AI-Lab API Server..."
echo ""

# Set PYTHONPATH to include user packages
export PYTHONPATH=/home/runner/.local/lib/python3.12/site-packages:$PYTHONPATH

# Start the API server
python3 scripts/api_server.py
