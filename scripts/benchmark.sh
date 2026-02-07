#!/bin/bash
# Benchmark AI response speed

echo "🔬 AI-Lab Performance Benchmark"
echo "================================"
echo ""

# Start API if not running
if ! pgrep -f "python.*api_server" > /dev/null; then
    echo "Starting API server..."
    cd ~/ai-forge
    source venv/bin/activate
    python scripts/api_server.py > /tmp/bench_api.log 2>&1 &
    API_PID=$!
    sleep 3
    echo "API started (PID: $API_PID)"
else
    echo "API already running"
fi

echo ""
echo "Testing response speed (3 requests)..."
echo ""

total=0
for i in 1 2 3; do
    echo -n "Test $i: "
    start=$(date +%s.%N)
    
    curl -s -X POST http://localhost:5174/api/chat \
        -H "Content-Type: application/json" \
        -d "{\"message\":\"hi\",\"history\":[]}" \
        --max-time 30 > /tmp/bench_response.txt 2>&1
    
    end=$(date +%s.%N)
    duration=$(echo "$end - $start" | bc)
    
    # Count tokens in response
    tokens=$(grep -o '"token"' /tmp/bench_response.txt | wc -l)
    
    echo "${duration}s (${tokens} tokens)"
    total=$(echo "$total + $duration" | bc)
done

echo ""
avg=$(echo "scale=2; $total / 3" | bc)
echo "Average: ${avg}s"
echo ""

# Get model info
model=$(curl -s http://localhost:11434/api/ps | python3 -c "import sys, json; m=json.load(sys.stdin)['models'][0]; print(m['name'])" 2>/dev/null)
echo "Model: $model"
echo "Threads: 4"
echo "Context: 1024"
echo ""
echo "✅ Benchmark complete!"
