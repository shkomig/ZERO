# 🧠 Zero Agent - Memory System Installation

## 📦 קבצים נדרשים:

### תיקיית memory/ (4 קבצים):
```
memory/
├── __init__.py
├── short_term_memory.py
├── rag_connector.py
└── memory_manager.py
```

### Main files:
- main_with_memory.py
- streaming_llm.py
- router_context_aware.py
- multi_model_executor.py

### קבצים קיימים (צריך להיות כבר):
- multi_model_llm.py (או streaming_llm.py יחליף)
- tool_filesystem.py
- tool_websearch.py
- tool_codeexecutor.py

---

## 🚀 התקנה:

### שלב 1: צור תיקיית memory
```powershell
cd C:\AI-ALL-PRO\ZERO
mkdir memory
```

### שלב 2: העתק קבצים
העתק את כל הקבצים מהלינקים למטה:

**memory/**
- memory/__init__.py
- memory/short_term_memory.py
- memory/rag_connector.py
- memory/memory_manager.py

**root/**
- main_with_memory.py
- streaming_llm.py (מחליף multi_model_llm.py)
- router_context_aware.py (מחליף model_router.py)
- multi_model_executor.py

### שלב 3: הרץ
```powershell
python main_with_memory.py
```

---

## ✅ בדיקה:

אם הכל עובד תראה:
```
🧠 Zero Agent - MEMORY EDITION
✨ FEATURES:
   • Context-Aware Router
   • Multi-Model Execution
   • Streaming Responses
   • 🧠 MEMORY SYSTEM (learns from conversations!)
```

---

## 🐛 פתרון בעיות:

### שגיאה: "No module named 'memory'"
→ ודא שהתיקייה memory/ קיימת עם כל 4 הקבצים

### שגיאה: "No module named 'streaming_llm'"
→ ודא ש-streaming_llm.py נמצא בתיקייה הראשית

### ⚠️ RAG not available
→ זה בסדר! Memory עובד גם בלי RAG
→ אם רוצה RAG: `docker-compose up -d` בתיקיית RAG

---

## 🎮 פקודות:

```
memory   - סטטיסטיקות זיכרון
context  - הצג context נוכחי
summary  - סיכום סשן
forget   - נקה זיכרונות ישנים
stats    - סטטיסטיקות מודלים
exit     - יציאה
```

---

## 📁 מבנה סופי:

```
C:\AI-ALL-PRO\ZERO\
├── memory/
│   ├── __init__.py
│   ├── short_term_memory.py
│   ├── rag_connector.py
│   └── memory_manager.py
├── main_with_memory.py
├── streaming_llm.py
├── router_context_aware.py
├── multi_model_executor.py
├── tool_filesystem.py
├── tool_websearch.py
└── tool_codeexecutor.py
```

בהצלחה! 🚀
