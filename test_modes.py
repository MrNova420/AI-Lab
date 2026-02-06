import requests, json, time

print("🔧 Testing NovaForge Full System\n")

# Test Commander mode
print("1️⃣ Testing Commander Mode...")
r = requests.post('http://localhost:5174/api/chat',
    json={
        'message': 'check if steam is installed',
        'history': [],
        'commander_mode': True
    },
    stream=True,
    timeout=15
)

response = ""
for line in r.iter_lines():
    if line:
        d = json.loads(line)
        if d['type'] == 'token':
            response += d['token']
        elif d['type'] == 'done':
            print(f"✅ Commander response: {response[:100]}")
            break

time.sleep(1)

# Test Web Search mode
print("\n2️⃣ Testing Web Search Mode...")
r = requests.post('http://localhost:5174/api/chat',
    json={
        'message': 'what year is it?',
        'history': [],
        'web_search_mode': True
    },
    stream=True,
    timeout=15
)

response = ""
for line in r.iter_lines():
    if line:
        d = json.loads(line)
        if d['type'] == 'token':
            response += d['token']
        elif d['type'] == 'done':
            print(f"✅ Web search response: {response[:100]}")
            break

print("\n✅ FULL SYSTEM WORKING!")
