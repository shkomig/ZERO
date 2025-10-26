# 🚀 Zero Agent API - Usage Guide

## 📦 Installation

### Step 1: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 2: Setup Google APIs (Optional)
If you want Gmail/Calendar:
1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 credentials
3. Download as `credentials.json`
4. Place in `C:\AI-ALL-PRO\ZERO\`

---

## 🚀 Start the API Server

```powershell
cd C:\AI-ALL-PRO\ZERO
python api_server.py
```

Server will start on: **http://localhost:8080**

API Docs: **http://localhost:8080/docs** (Interactive!)

---

## 📡 API Endpoints

### 1️⃣ **Chat with Zero**

**Endpoint:** `POST /api/chat`

```python
import requests

response = requests.post('http://localhost:8080/api/chat', json={
    "message": "Explain quantum computing",
    "model": "fast",  # Optional: fast, smart, coder, balanced
    "use_memory": True
})

print(response.json())
# {
#   "response": "Quantum computing is...",
#   "model_used": "fast",
#   "duration": 2.5
# }
```

**JavaScript:**
```javascript
fetch('http://localhost:8080/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "What's 2+2?",
        use_memory: true
    })
})
.then(r => r.json())
.then(data => console.log(data.response));
```

**cURL:**
```bash
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Zero!", "use_memory": true}'
```

---

### 2️⃣ **Email Operations**

**Endpoint:** `POST /api/tools/email`

**Search emails:**
```python
response = requests.post('http://localhost:8080/api/tools/email', json={
    "action": "search",
    "query": "from:john@example.com",
    "count": 10
})
```

**Get recent emails:**
```python
response = requests.post('http://localhost:8080/api/tools/email', json={
    "action": "recent",
    "count": 5
})
```

**Send email:**
```python
response = requests.post('http://localhost:8080/api/tools/email', json={
    "action": "send",
    "to": "friend@example.com",
    "subject": "Hello!",
    "body": "This is from Zero Agent"
})
```

---

### 3️⃣ **Calendar Operations**

**Endpoint:** `POST /api/tools/calendar`

**Today's events:**
```python
response = requests.post('http://localhost:8080/api/tools/calendar', json={
    "action": "today"
})
```

**This week:**
```python
response = requests.post('http://localhost:8080/api/tools/calendar', json={
    "action": "week"
})
```

**Create event:**
```python
response = requests.post('http://localhost:8080/api/tools/calendar', json={
    "action": "create",
    "summary": "Meeting with team",
    "start": "2025-10-25T14:00:00",
    "end": "2025-10-25T15:00:00",
    "description": "Discuss Q4 goals"
})
```

---

### 4️⃣ **Database Operations**

**Endpoint:** `POST /api/tools/database`

**Execute query:**
```python
response = requests.post('http://localhost:8080/api/tools/database', json={
    "action": "query",
    "query": "SELECT * FROM users LIMIT 10",
    "db_path": "workspace/data.db"
})
```

**List tables:**
```python
response = requests.post('http://localhost:8080/api/tools/database', json={
    "action": "tables",
    "db_path": "workspace/data.db"
})
```

**Show schema:**
```python
response = requests.post('http://localhost:8080/api/tools/database', json={
    "action": "schema",
    "table_name": "users",
    "db_path": "workspace/data.db"
})
```

---

### 5️⃣ **Memory Operations**

**Get stats:**
```python
response = requests.get('http://localhost:8080/api/memory/stats')
print(response.json())
```

**Get context:**
```python
response = requests.get('http://localhost:8080/api/memory/context', 
    params={"query": "what did we discuss about AI?"})
```

**Clear old memories:**
```python
response = requests.post('http://localhost:8080/api/memory/clear',
    params={"days": 30})
```

---

## 🌊 WebSocket Streaming (Real-time)

For **streaming responses** (like ChatGPT):

**Python:**
```python
import websockets
import asyncio
import json

async def chat_stream():
    uri = "ws://localhost:8080/ws/chat"
    
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "message": "Explain AI in simple terms",
            "model": "fast"
        }))
        
        # Receive streaming tokens
        full_response = ""
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "token":
                print(data["content"], end="", flush=True)
                full_response += data["content"]
            
            elif data["type"] == "done":
                print(f"\n\nModel: {data['model']}")
                break

asyncio.run(chat_stream())
```

**JavaScript:**
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/chat');

ws.onopen = () => {
    ws.send(JSON.stringify({
        message: "Tell me about space",
        model: "smart"
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.type === 'token') {
        process.stdout.write(data.content);
    } else if (data.type === 'done') {
        console.log(`\nDone! Model: ${data.model}`);
    }
};
```

---

## 🔌 Integration Examples

### Cursor Integration

Create `.cursorrules` or use Cursor's API:

```python
# cursor_zero_integration.py
import requests

def ask_zero(query: str) -> str:
    """Ask Zero Agent from Cursor"""
    response = requests.post('http://localhost:8080/api/chat', json={
        "message": query,
        "use_memory": True
    })
    return response.json()['response']

# Usage in Cursor:
# result = ask_zero("Explain this code")
```

---

### VS Code Extension

```javascript
// extension.js
const vscode = require('vscode');
const axios = require('axios');

async function askZero(query) {
    const response = await axios.post('http://localhost:8080/api/chat', {
        message: query,
        use_memory: true
    });
    
    return response.data.response;
}

// Register command
vscode.commands.registerCommand('zero.ask', async () => {
    const input = await vscode.window.showInputBox({
        prompt: 'Ask Zero Agent'
    });
    
    if (input) {
        const answer = await askZero(input);
        vscode.window.showInformationMessage(answer);
    }
});
```

---

### Python Client Library

```python
# zero_client.py
import requests

class ZeroClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def chat(self, message, model=None, use_memory=True):
        """Chat with Zero"""
        response = requests.post(f"{self.base_url}/api/chat", json={
            "message": message,
            "model": model,
            "use_memory": use_memory
        })
        return response.json()
    
    def search_emails(self, query, count=10):
        """Search emails"""
        response = requests.post(f"{self.base_url}/api/tools/email", json={
            "action": "search",
            "query": query,
            "count": count
        })
        return response.json()
    
    def today_calendar(self):
        """Get today's calendar"""
        response = requests.post(f"{self.base_url}/api/tools/calendar", json={
            "action": "today"
        })
        return response.json()

# Usage:
zero = ZeroClient()
response = zero.chat("What's the weather?")
print(response['response'])
```

---

## 🧪 Testing

**Health Check:**
```bash
curl http://localhost:8080/health
```

**Interactive Docs:**
Go to: http://localhost:8080/docs

Try all endpoints directly in the browser!

---

## 🔒 Security (Production)

For production deployment:

1. **Add Authentication:**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/chat")
async def chat(request: ChatRequest, token = Depends(security)):
    # Verify token
    if not verify_token(token.credentials):
        raise HTTPException(status_code=401)
    # ... rest of code
```

2. **Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):
    # ... code
```

3. **HTTPS:**
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem"
)
```

---

## 📊 Monitoring

Check server status:
```python
import requests

status = requests.get('http://localhost:8080/')
print(status.json())

# Shows:
# - Online status
# - Available features
# - All endpoints
```

---

## 🎯 Next Steps

1. **Try the Interactive Docs:** http://localhost:8080/docs
2. **Test with curl/Postman**
3. **Build your integration** (Cursor, VS Code, etc.)
4. **Add more tools** as needed

---

**Happy coding!** 🚀
