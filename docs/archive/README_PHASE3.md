# 🚀 Zero Agent - Phase 3: Smart Orchestrator

## מה חדש?

### ✨ Orchestrator v2 - החכם יותר

הוספנו orchestrator חדש עם יכולות מתקדמות:

---

## 🎯 יכולות חדשות

### 1️⃣ **ניתוח משימות (Task Analysis)**
```python
# הOrchestrator מנתח כל משימה:
- מורכבות: simple / medium / complex
- קטגוריה: question / file_operation / web_search / code
- כלים נדרשים: [filesystem, web_search, ...]
- מספר שלבים משוער: 1-10
```

### 2️⃣ **תכנון חכם (Smart Planning)**
```python
# יוצר תוכנית ביצוע לפי מורכבות:

משימה פשוטה:
[
    {"step": 1, "action": "answer", "description": "ענה ישירות"}
]

משימה מורכבת:
[
    {"step": 1, "action": "think", "description": "הבן דרישות"},
    {"step": 2, "action": "filesystem", "description": "צור קובץ"},
    {"step": 3, "action": "web_search", "description": "חפש מידע"},
    {"step": 4, "action": "answer", "description": "סכם תוצאות"}
]
```

### 3️⃣ **היסטוריה (History Tracking)**
```python
# שומר כל ביצוע:
{
    "timestamp": "2025-10-22T...",
    "task": "Create a file...",
    "plan": [...],
    "result": "..."
}
```

---

## 📖 איך להשתמש?

### דוגמה בסיסית:
```python
from orchestrator_v2 import SmartOrchestrator

# יצירה
orchestrator = SmartOrchestrator(llm, tools, workspace)

# ביצוע משימה
result = orchestrator.execute("Create a Python script")

# בדיקת תוצאה
if result["success"]:
    print(f"Complexity: {result['analysis']['complexity']}")
    print(f"Steps: {len(result['plan'])}")
    print(f"Result: {result['result']}")
```

### הרצת הטסטים:
```bash
# בדיקת הOrchestrator החדש
python test_orchestrator_v2.py
```

---

## 🔄 ההבדל מהגרסה הקודמת

### ❌ Orchestrator v1 (SimpleOrchestrator):
```python
# פשוט מדי - אין תכנון
execute(task) → ask LLM → return answer
```

### ✅ Orchestrator v2 (SmartOrchestrator):
```python
# חכם - מתכנן ומנתח
execute(task) → 
    1. analyze_task()      # הבן מה צריך
    2. create_plan()       # תכנן שלבים
    3. execute_plan()      # בצע
    4. save_to_history()   # שמור
```

---

## 📊 דוגמאות ביצוע

### דוגמה 1: משימה פשוטה
```
Task: "What is 2+2?"

Analysis:
  ✓ Complexity: simple
  ✓ Category: question
  ✓ Tools needed: []

Plan:
  1. Answer directly

Result: "2+2 equals 4"
```

### דוגמה 2: משימה מורכבת
```
Task: "Search for Python tutorials and create a summary"

Analysis:
  ✓ Complexity: complex
  ✓ Category: mixed
  ✓ Tools needed: [web_search, filesystem]

Plan:
  1. Think - Understand what to search
  2. web_search - Find Python tutorials
  3. think - Analyze results
  4. filesystem - Create summary file
  5. answer - Confirm completion

Result: "Created summary.txt with 5 top tutorials"
```

---

## 🎯 השלב הבא

עכשיו שיש לנו orchestrator חכם, נוסיף:

1. **Tools מלאים** - filesystem, web_search, code_executor
2. **Memory System** - זיכרון בין שיחות
3. **Error Recovery** - טיפול בשגיאות וניסיון חוזר

---

## 📁 מבנה הקבצים

```
Zero/
├── orchestrator_v2.py          ← חדש! Orchestrator חכם
├── test_orchestrator_v2.py     ← חדש! טסטים
├── simple_llm.py               ← קיים
├── workspace/
│   └── history.json            ← חדש! היסטוריה
└── README_PHASE3.md            ← אתה כאן
```

---

## ✅ מה עובד

- [x] ניתוח משימות
- [x] תכנון ביצוע
- [x] שמירת היסטוריה
- [ ] Tools מלאים (בשלב הבא)
- [ ] Error recovery (בשלב הבא)
- [ ] Memory system (בשלב הבא)

---

**עבודה טובה! המערכת מתקדמת 🚀**
