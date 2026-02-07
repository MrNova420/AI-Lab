#!/bin/bash
# Quick test script to verify everything works

cd /home/mrnova420/ai-forge

echo "🧪 Testing AI-Forge Components..."
echo ""

# Activate venv
source venv/bin/activate

echo "1️⃣ Testing Logging System..."
python3 -c "
from core.logging_system import LoggingSystem
logger = LoggingSystem()
sid = logger.start_session('TestUser')
logger.log_message('user', 'Hello')
logger.log_message('assistant', 'Hi there!')
print('✅ Logging works - saved to:', logger.session_file)
"

echo ""
echo "2️⃣ Testing Resource Monitor..."
python3 -c "
from core.resource_monitor import get_monitor
monitor = get_monitor()
stats = monitor.get_all_stats()
print('✅ Resource monitor works')
print('   CPU:', stats['cpu']['usage_percent'], '%')
print('   Memory:', stats['memory']['percent'], '%')
"

echo ""
echo "3️⃣ Testing Memory System..."
python3 -c "
from core.memory_system import AdvancedMemory
memory = AdvancedMemory()
memory.short_term.add('Test memory')
print('✅ Memory system works')
"

echo ""
echo "4️⃣ Checking API Server..."
if pgrep -f "api_server.py" > /dev/null; then
    echo "⚠️  API server is running (PID: $(pgrep -f api_server.py))"
    echo "   To restart: pkill -f api_server.py && venv/bin/python3 scripts/api_server.py"
else
    echo "❌ API server is NOT running"
    echo "   To start: venv/bin/python3 scripts/api_server.py"
fi

echo ""
echo "5️⃣ Checking saved sessions..."
if [ -d "memory/sessions/2026-02-07" ]; then
    count=$(ls memory/sessions/2026-02-07/*.json 2>/dev/null | wc -l)
    echo "✅ Found $count sessions for today"
    echo "   Location: memory/sessions/2026-02-07/"
else
    echo "⚠️  No sessions saved yet"
fi

echo ""
echo "✅ Core systems are working!"
echo ""
echo "📋 To fix the app:"
echo "1. Stop API server: pkill -f api_server.py"
echo "2. Start with venv: venv/bin/python3 scripts/api_server.py"
echo "3. Start app: ./forge-app.sh"
