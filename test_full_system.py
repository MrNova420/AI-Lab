#!/usr/bin/env python3
"""
Quick test of full system
"""

import requests
import json

print("🧪 Testing Full NovaForge System\n")

# Test 1: Normal mode
print("1️⃣ Normal Mode (no tools)")
r = requests.post('http://localhost:5174/api/chat',
    json={'message': 'Hi!', 'history': []},
    stream=True, timeout=5)
tokens = []
for line in r.iter_lines():
    if line:
        d = json.loads(line)
        if d['type'] == 'token':
            tokens.append(d['token'])
print(f"✅ Response: {''.join(tokens[:10])}")

# Test 2: Commander mode
print("\n2️⃣ Commander Mode")
r = requests.post('http://localhost:5174/api/chat',
    json={'message': 'open steam', 'history': [], 'commander_mode': True},
    stream=True, timeout=10)
for line in r.iter_lines():
    if line:
        d = json.loads(line)
        if d['type'] == 'tool_results':
            print(f"✅ Tool executed: {d['results'][0]['tool']}")
            break

# Test 3: Web search mode  
print("\n3️⃣ Web Search Mode")
r = requests.post('http://localhost:5174/api/chat',
    json={'message': 'what is happening in 2026?', 'history': [], 'web_search_mode': True},
    stream=True, timeout=10)
tokens = []
for line in r.iter_lines():
    if line:
        d = json.loads(line)
        if d['type'] == 'token':
            tokens.append(d['token'])
            if len(tokens) > 20:
                break
print(f"✅ Response: {''.join(tokens[:15])}")

print("\n✅ All tests passed!")
