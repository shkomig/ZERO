"""
דוגמה לשילוב Zero Agent בפרויקטים שלך
"""

import requests


class ZeroAgent:
    """קלאס נוח לעבודה עם Zero Agent"""
    
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def ask(self, question: str, model: str = None, use_memory: bool = True) -> str:
        """שאל שאלה - תשובה מיידית"""
        response = requests.post(f"{self.base_url}/api/chat", 
            json={
                "message": question,
                "model": model,
                "use_memory": use_memory
            })
        return response.json()['response']
    
    def code(self, task: str) -> str:
        """בקש קוד - משתמש במודל המתכנת"""
        return self.ask(task, model="coder")
    
    def explain(self, topic: str) -> str:
        """הסבר דבר - משתמש במודל החכם"""
        return self.ask(topic, model="smart")
    
    def quick(self, question: str) -> str:
        """תשובה מהירה - מודל מהיר"""
        return self.ask(question, model="fast")


# ============================================================================
# דוגמאות שימוש
# ============================================================================

def example_1_basic():
    """דוגמה בסיסית"""
    zero = ZeroAgent()
    
    answer = zero.ask("מה זה Python?")
    print(answer)


def example_2_coding():
    """דוגמה לכתיבת קוד"""
    zero = ZeroAgent()
    
    code = zero.code("כתוב פונקציה Python לחישוב מספרי פיבונאצ'י")
    print(code)


def example_3_explanation():
    """דוגמה להסבר"""
    zero = ZeroAgent()
    
    explanation = zero.explain("איך עובדים transformers בטבע AI?")
    print(explanation)


def example_4_multiple_questions():
    """דוגמה למספר שאלות"""
    zero = ZeroAgent()
    
    questions = [
        "מה זה machine learning?",
        "כיצד עובדים neural networks?",
        "מה ההבדל בין AI ל-ML?"
    ]
    
    for q in questions:
        print(f"\n❓ {q}")
        print(f"💭 {zero.quick(q)}\n")


def example_5_project_helper():
    """דוגמה - עוזר בפרויקט"""
    zero = ZeroAgent()
    
    # תחילת פרויקט
    architecture = zero.code("תכנן ארכיטקטורה ל-app ניהול משימות עם Python Flask")
    print("📐 ארכיטקטורה:", architecture)
    
    # הסבר מושג
    concept = zero.explain("איך עובד RESTful API?")
    print("\n📚 הסבר:", concept)


if __name__ == "__main__":
    # נסה אחת מהפונקציות:
    example_1_basic()
    # example_2_coding()
    # example_3_explanation()
    # example_4_multiple_questions()
    # example_5_project_helper()

