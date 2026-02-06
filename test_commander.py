#!/usr/bin/env python3
"""Test Commander Mode with Smart AI"""

import requests
import json

print("🧪 Testing Smart Commander AI...\n")

# Test 1: Normal chat (should just respond)
print("Test 1: Normal question")
print("User: What is Steam?")
response = requests.post(
    'http://localhost:5174/api/chat',
    json={'message': 'What is Steam?', 'history': [], 'commander_mode': False},
    stream=True,
    timeout=10
)
print("AI: ", end='')
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if data['type'] == 'token':
            print(data['token'], end='', flush=True)
print("\n")

# Test 2: Commander mode - open app
print("\nTest 2: Commander mode action")
print("User: Open Steam")
response = requests.post(
    'http://localhost:5174/api/chat',
    json={'message': 'Open Steam', 'history': [], 'commander_mode': True},
    stream=True,
    timeout=15
)
print("AI: ", end='')
full_resp = ""
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        if data['type'] == 'token':
            print(data['token'], end='', flush=True)
            full_resp += data['token']
        elif data['type'] == 'tool_results':
            print("\n\n" + data.get('formatted', ''))
print("\n")

print("✅ Tests complete!")
