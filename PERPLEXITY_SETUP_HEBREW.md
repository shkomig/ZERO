# 🚀 הגדרת Perplexity API - מדריך מהיר בעברית

## ✅ מה עשינו כבר:

1. ✓ יצרנו `tool_perplexity_search.py` - כלי חיפוש Perplexity
2. ✓ עדכנו `tool_websearch_improved.py` - משלב Perplexity אוטומטית
3. ✓ הכל מוכן לעבודה!

---

## 📝 מה אתה צריך לעשות:

### שלב 1: צור קובץ `.env` (אם אין)

בתיקיית הפרויקט (`C:\AI-ALL-PRO\ZERO\`), צור קובץ חדש בשם:
```
.env
```

(שים לב - הקובץ מתחיל בנקודה!)

---

### שלב 2: הוסף את ה-API Key

פתח את `.env` והדבק את זה (החלף עם המפתח האמיתי שלך):

```bash
# Perplexity API Key
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Ollama (אם עדיין לא קיים)
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.1:8b
```

**חשוב:** ודא שאין רווחים לפני/אחרי המפתח!

---

### שלב 3: התקן תלויות (אם צריך)

```bash
pip install python-dotenv requests
```

---

### שלב 4: בדוק שזה עובד!

```bash
python tool_perplexity_search.py
```

**תראה:**
```
======================================================================
Testing Perplexity AI Search
======================================================================

[Test 1] Simple query: 'What is AI?'
✓ Success!
Answer length: 450 chars
Citations: 3

[Test 2] Real-time query: 'Latest AI news'
✓ Success!
Citations: 5

Perplexity AI Search is working!
======================================================================
```

---

### שלב 5: הפעל מחדש את API Server

```bash
python api_server.py
```

תראה בהתחלה:
```
[WebSearch] ✓ Perplexity AI enabled - real-time search active!
```

---

## 🎯 איך להשתמש

עכשיו פשוט שאל שאלות כרגיל!

המערכת **אוטומטית** תשתמש ב-Perplexity כשמתאים:

### דוגמאות שמפעילות Perplexity:
```
✓ "What is the latest AI news?"
✓ "Who is Sam Altman?"
✓ "Explain quantum computing"
✓ "Recent developments in AI"
✓ "Current events in technology"
✓ "Compare GPT-4 and Claude"
```

### דוגמאות שמשתמשות ב-DuckDuckGo (פשוט יותר):
```
✓ "Python tutorial" (חיפוש רגיל)
✓ "Best restaurants in Tel Aviv" (לא צריך AI)
```

### דוגמאות מניות (Yahoo Finance):
```
✓ "Price of NVDA stock"
✓ "Current price TSLA"
```

---

## 📊 מה תקבל מ-Perplexity?

**לפני (DuckDuckGo):**
```
תוצאות חיפוש:
1. Link 1
2. Link 2
3. Link 3
```

**אחרי (Perplexity AI):**
```
🤖 Perplexity AI (Real-time)

[תשובה מפורטת ומדויקת עם מידע עדכני]

📚 Sources (5):
1. https://source1.com
2. https://source2.com
3. https://source3.com
4. https://source4.com
5. https://source5.com
```

---

## 💰 עלויות

**Perplexity מחיר:** ~$5 למיליון טוקנים

**חיפוש ממוצע:**
- שאלה: ~50 טוקנים
- תשובה: ~500 טוקנים
- **סה"כ:** ~550 טוקנים

**עלות לחיפוש:** $0.00275

**בפועל:** ~360 חיפושים ב-$1! 💸

---

## 🔧 Troubleshooting

### אני לא רואה את ההודעה "[WebSearch] ✓ Perplexity AI enabled"

**פתרון:**
1. בדוק שהקובץ `.env` קיים בתיקיית הפרויקט
2. בדוק שהמפתח נכון (בלי רווחים)
3. הפעל מחדש את API Server

### שגיאה: "Invalid API key"

**פתרון:**
1. לך ל: https://www.perplexity.ai/settings/api
2. צור API key חדש
3. העתק אותו בדיוק כמו שהוא
4. הדבק ב-`.env`

### השאלה שלי לא משתמשת ב-Perplexity

**פתרון:**
שאל עם מילות מפתח כמו:
- "latest", "recent", "current"
- "who is", "what is", "explain"
- "news", "today", "compare"

---

## 📍 מיקום הקבצים

```
C:\AI-ALL-PRO\ZERO\
├── .env                           ← צור קובץ זה! (שים את ה-API key)
├── tool_perplexity_search.py      ← כלי Perplexity
├── tool_websearch_improved.py     ← עודכן עם Perplexity
└── api_server.py                  ← הפעל מחדש אותו
```

---

## ✨ סיכום

1. **צור `.env`** עם המפתח שלך
2. **הפעל מחדש** את API Server
3. **שאל שאלות** כרגיל
4. **תקבל תשובות** עם מקורות בזמן אמת!

---

**צריך עזרה?** פשוט שאל! 🚀

