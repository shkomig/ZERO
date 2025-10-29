#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""בדיקות קריטיות ליכולת ההיגיון והכתיבה של Mixtral 8x7B."""

import json
import sys
import time
from pathlib import Path

import requests


try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    pass


QUESTIONS = [
    "בבניין משרדים יש 10 קומות, ולכל קומה יש 20 חלונות. אם מחיר כל חלון שבור הוא 300 ש""ח לתיקון, וכיום יש 15 חלונות שבורים בבניין כולו, כמה חלונות תקינים יש בבניין? הצג את החישוב המדויק שלך שלב אחר שלב.",
    "הסבר את ההבדל בין Latency ל-Throughput תוך שימוש במונחים העבריים המקובלים (כפי שמופיעים במילון המונחים שלך).",
    "כתוב מכתב התפטרות רשמי לעמית לעבודה (בטון פורמלי ומכובד). במכתב, עליך לציין שאתה עוזב כדי להקים מיזם סטארט-אפ בתחום הקפה המקביל (Parallel Coffee). המכתב צריך להיות מחולק ל-3 פסקאות ברורות: פנייה ופרישה, הבעת תודה, ואיחול הצלחה לעתיד."
]


def ask(question: str) -> dict:
    response = requests.post(
        "http://localhost:8080/api/chat",
        json={"message": question, "conversation_history": []},
        timeout=90,
    )
    response.raise_for_status()
    return response.json()


def main() -> int:
    print("=== בדיקות היגיון ושפה - Mixtral 8x7B ===", flush=True)
    results = []

    for idx, question in enumerate(QUESTIONS, start=1):
        print("-" * 90)
        print(f"בדיקה {idx}: {question}")

        started = time.time()
        try:
            payload = ask(question)
        except Exception as exc:  # noqa: BLE001
            print(f"✗ שגיאה בבדיקה {idx}: {exc}")
            continue

        model_used = payload.get("model_used", "unknown")
        duration = payload.get("duration", 0.0)
        answer = payload.get("response", "").strip()

        elapsed = time.time() - started
        print(f"מודל: {model_used} | זמן API: {duration:.2f}s | זמן כולל: {elapsed:.2f}s")
        print("תשובה:\n", answer)
        results.append({
            "model": model_used,
            "duration": duration,
            "question": question,
            "answer": answer,
        })

    print("-" * 90)
    output_path = Path("tests") / "run_logic_suite_results.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[✓] תוצאות נשמרו אל {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

