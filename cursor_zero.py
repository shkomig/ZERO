"""
Cursor <-> Zero Bridge
Run this in background, adds "Ask Zero" to Cursor
"""

from fastapi import FastAPI
import requests
import uvicorn

app = FastAPI()

@app.post("/ask")
async def ask_zero(question: dict):
    # Forward to Zero
    response = requests.post('http://localhost:8080/api/chat',
        json={"message": question['text']}
    )
    return response.json()

if __name__ == "__main__":
    print("🔗 Cursor-Zero Bridge running on :8081")
    uvicorn.run(app, host="0.0.0.0", port=8081)