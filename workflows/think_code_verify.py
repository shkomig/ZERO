import sys
import requests


API_URL = "http://localhost:8080/api/chat"


def call_zero(message: str, model: str | None = None, history=None) -> dict:
    payload = {"message": message, "use_memory": True}
    if model:
        payload["model"] = model
    if history:
        payload["conversation_history"] = history
    resp = requests.post(API_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def run(task: str):
    history = []

    # 1) THINK (smart / reasoning)
    think_prompt = f"Analyze and plan step-by-step in Hebrew. Task: {task}\nDeliver a concise plan and key decisions."
    r1 = call_zero(think_prompt, model="smart", history=history)
    plan = r1.get("response", "")
    history.append({"role": "user", "content": think_prompt})
    history.append({"role": "assistant", "content": plan})

    # 2) CODE (coder)
    code_prompt = (
        "יישם בקוד את התוכנית הבאה בצורה נקייה ומתועדת (Python אם רלוונטי):\n\n"
        + plan
        + "\n\nעמוד בדרישות ובצע בדיקות בסיסיות אם יש מקום."
    )
    r2 = call_zero(code_prompt, model="coder", history=history)
    code_out = r2.get("response", "")
    history.append({"role": "user", "content": code_prompt})
    history.append({"role": "assistant", "content": code_out})

    # 3) VERIFY (smart)
    verify_prompt = (
        "בדוק בקפדנות את הפתרון מבחינת נכונות, ביצועים,边 ומקרי קצה. הצע תיקונים קצרים במידת הצורך."
        "\n\nפתרון שנוצר:\n" + code_out
    )
    r3 = call_zero(verify_prompt, model="smart", history=history)
    verify = r3.get("response", "")

    print("\n=== PLAN (SMART) ===\n" + plan)
    print("\n=== CODE (CODER) ===\n" + code_out)
    print("\n=== VERIFY (SMART) ===\n" + verify)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python workflows/think_code_verify.py \"משימה\"")
        sys.exit(1)
    run(" ".join(sys.argv[1:]))


