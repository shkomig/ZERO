"""
דוגמה לשיחה עם Zero Agent בשיטת Streaming
"""
import websockets
import asyncio
import json

async def chat_with_zero(question: str):
    """שיחה בזמן אמת עם Zero"""
    uri = "ws://localhost:8080/ws/chat"
    
    print(f"🤖 שואל: {question}\n")
    print("💭 Zero עונה:")
    
    try:
        async with websockets.connect(uri) as websocket:
            # שולח שאלה
            await websocket.send(json.dumps({
                "message": question,
                "model": "fast",
                "use_memory": True
            }))
            
            # מקבל תשובה תוך כדי
            full_response = ""
            async for message in websocket:
                data = json.loads(message)
                
                if data["type"] == "token":
                    # הדפס מיידי של כל מילה
                    print(data["content"], end="", flush=True)
                    full_response += data["content"]
                
                elif data["type"] == "done":
                    print(f"\n\n✅ סיום! מודל: {data['model']}")
                    break
        
        return full_response
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return None


async def conversation():
    """שיחה עם Zero"""
    print("=" * 50)
    print("🚀 Zero Agent - Streaming Chat")
    print("=" * 50)
    
    while True:
        question = input("\n💬 שאלה שלך (או 'quit' לסיום): ")
        
        if question.lower() in ['quit', 'exit', 'יציאה']:
            print("👋 להתראות!")
            break
        
        await chat_with_zero(question)


if __name__ == "__main__":
    asyncio.run(conversation())

