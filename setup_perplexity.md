# 🚀 הגדרת Perplexity API - מדריך מהיר

## שלב 1: הכנס את ה-API Key

פתח את הקובץ `.env` והחלף את:
```
PERPLEXITY_API_KEY=your_perplexity_key_here
```

עם המפתח האמיתי שלך:
```
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxxxxxxxxxxx
```

---

## שלב 2: התקן תלויות (אם צריך)

```bash
pip install requests python-dotenv
```

---

## שלב 3: בדוק שזה עובד

```bash
python tool_perplexity_search.py
```

אמור לראות:
```
======================================================================
Testing Perplexity AI Search
======================================================================

[Test 1] Simple query: 'What is AI?'
✓ Success!
Answer length: XXX chars
Citations: X

...

Perplexity AI Search is working!
```

---

## שלב 4: שלב ב-Zero Agent

הקובץ `tool_websearch_improved.py` עודכן אוטומטית להשתמש ב-Perplexity.

פשוט הפעל מחדש את ה-API Server:
```bash
python api_server.py
```

---

## שימוש

עכשיו תוכל לשאול:
- "What is the latest news about AI?" → תשובה מ-Perplexity עם מקורות
- "latest developments in quantum computing" → מידע עדכני
- "who is Sam Altman?" → תשובה מקיפה

---

## מודלים זמינים

| מודל | מהירות | איכות | מתי להשתמש |
|------|--------|-------|------------|
| `fast` | ⚡⚡⚡ | ⭐⭐⭐ | רוב השאלות |
| `balanced` | ⚡⚡ | ⭐⭐⭐⭐ | שאלות בינוניות |
| `quality` | ⚡ | ⭐⭐⭐⭐⭐ | מחקר מעמיק |

ברירת מחדל: `fast` (מספיק לרוב המקרים!)

---

## בדיקת עלות

Perplexity מחיר: ~$5 למיליון טוקנים

חיפוש ממוצע:
- שאלה: ~50 טוקנים
- תשובה: ~500 טוקנים
- סה"כ: ~550 טוקנים = $0.00275 לחיפוש

**~360 חיפושים ב-$1!** 🎯

---

## Troubleshooting

### שגיאה: "Invalid API key"
✓ בדוק שהמפתח ב-`.env` נכון
✓ בדוק שאין רווחים בתחילת/סוף המפתח

### שגיאה: "Rate limit exceeded"
✓ חכה 1-2 דקות
✓ בדוק את המכסה שלך ב-Perplexity dashboard

### החיפוש לא עובד
✓ הפעל מחדש את API Server
✓ בדוק: `python tool_perplexity_search.py`

---

**הכל מוכן!** פשוט שאל שאלות ותקבל תשובות בזמן אמת עם מקורות! 🚀

