ZERO - המשך פיתוח מודול AI Model Manager
מטרה
לממש מערכת ניהול חכמה וחלקה למודלים המקומיים שלך (DeepSeek-R1, Llama 3.1-8B, Qwen 2.5-Coder-32B) בתוך ZERO, עם ניהול דינמי של בחירת מודל, ניהול חלון הקשר גדול, טיפול בזרימת תשובות וטעינת שגיאות.

הנחיות לפיתוח המודל מנג'ר
1. יצירת מחלקת ModelManager ב-src/ai/model_manager.py
תומכת בשלוש המודלים כמשאבים עם הפונקציות הבאות:

load_model(model_name: str): טעינת המודל המתאים דרך Ollama

query_model(model_name: str, input_text: str, context: str, stream: bool): שליחת שאילתא עם הקשר

switch_model(task_type: str): בחירת המודל לפי סוג מטלה (קוד, ניתוח, שאלות מהירות)

ניהול חלון הקשר (Context Window) עם חיתוך מידע אם חורג מ-128K tokens

טיפול בחריגות ושגיאות עם רטריאת עד 3 ניסיונות

תיעוד הרצת המודלים (למשל logging זמן תגובה, נפח טוקנים)

2. חיבור לממשק Ollama
שימוש בספריית ollama-python לתקשורת למודל המקומי

תמיכה ב-streaming לקבלת תשובות במהלך השיחה

דוגמה לקוד בסיסי
python
import asyncio
from ollama import OllamaClient, OllamaError
import logging

class ModelManager:
    def __init__(self):
        self.client = OllamaClient(base_url="http://localhost:11434")
        self.models = {
            "deepseek": "deepseek-r1:32b",
            "llama": "llama3.1:8b",
            "qwen": "qwen2.5-coder:32b"
        }
        self.logger = logging.getLogger("ModelManager")
    
    def switch_model(self, task_type: str) -> str:
        if task_type == "trading":
            return self.models["deepseek"]
        elif task_type == "code":
            return self.models["qwen"]
        else:
            return self.models["llama"]

    async def query_model(self, model_name: str, input_text: str, context: str, stream: bool = False) -> str:
        prompt = f\"\"\"System: Use the following context to answer the query:\n{context}\nQuery:\n{input_text}\"\"\"
        for attempt in range(3):
            try:
                response = await self.client.chat(
                    model=model_name,
                    messages=[{"role": "system", "content": prompt}],
                    stream=stream
                )
                if stream:
                    # Implement streaming handler if needed
                    pass
                else:
                    return response["message"]["content"]
            except OllamaError as e:
                self.logger.error(f\"Model query failed on attempt {attempt+1}: {e}\")
                await asyncio.sleep(2 ** attempt)
        raise Exception("All model query attempts failed")
טיפים לפיתוח
ודא שהדינמיות של בחירת המודל מבוססת על מטלה ברורה

נהל את גודל חלון ההקשר בקפידה כדי למנוע טעויות של Overflow

אפשר שרידות בשירות (Retry) ונהל טעויות gracefully

יישם מדידת ביצועים וניתוח (Latency, Token usage)

שלב במערכת ניהול זיכרון לטיפול בהיסטוריית שיחות ואחסון בטוח

שמור על ממשק אסינכרוני לחסכון במשאבים וביצוע חכם

