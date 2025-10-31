# 📝 הוראות ליצירת קובץ .env

## ✅ הקובץ נוצר!

קובץ `.env` נוצר בתיקיית הפרויקט.

---

## 🔧 עכשיו עשה את זה:

### שלב 1: פתח את הקובץ `.env`

ב-VS Code או Notepad:
```
C:\AI-ALL-PRO\ZERO\.env
```

---

### שלב 2: ערוך את השורה

תמצא:
```
PERPLEXITY_API_KEY=PASTE_YOUR_KEY_HERE
```

**החלף** את `PASTE_YOUR_KEY_HERE` עם ה-API key האמיתי שלך!

**דוגמה:**
```
PERPLEXITY_API_KEY=pplx-1a2b3c4d5e6f7g8h9i0j
```

---

### שלב 3: שמור את הקובץ

לחץ `Ctrl+S` או File → Save

---

### שלב 4: בדוק שזה עובד

הרץ:
```bash
python quick_test_perplexity.py
```

אמור לראות:
```
✓ .env exists
✓ PERPLEXITY_API_KEY found in .env
✓ Loaded: pplx-xxxxx...xxx
✓ Perplexity API is working!
```

---

### שלב 5: הפעל מחדש API Server

```bash
python api_server.py
```

חפש:
```
[WebSearch] ✓ Perplexity AI enabled - real-time search active!
```

---

## 🎯 סיימת!

עכשיו המערכת תשתמש ב-Perplexity לחיפוש בזמן אמת! 🚀

---

## 💡 איפה המפתח שלי?

אם אין לך עדיין API key:
1. לך ל: https://www.perplexity.ai/settings/api
2. צור חשבון (חינם להתחלה)
3. לחץ "Generate API Key"
4. העתק את המפתח
5. הדבק ב-`.env`

---

## 🔒 אבטחה

הקובץ `.env` מכיל מידע רגיש!
- ✅ לא משותף ב-Git (אוטומטי)
- ✅ רק במחשב שלך
- ✅ אל תשתף את המפתח

---

**צריך עזרה?** הרץ: `python quick_test_perplexity.py`

