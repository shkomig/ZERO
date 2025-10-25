# 📧 מדריך הגדרת Gmail API

## ❌ הבעיה
הממשק מחזיר שגיאה:
```
credentials.json not found
```

## ✅ הפתרון - הגדרת Gmail API

### שלב 1️⃣: יצירת פרויקט ב-Google Cloud Console

1. פתח: https://console.cloud.google.com/
2. לחץ על "New Project"
3. תן שם לפרויקט: `Zero Agent Gmail`
4. לחץ "Create"

### שלב 2️⃣: הפעלת Gmail API

1. בתפריט השמאלי, לך ל-**APIs & Services** → **Library**
2. חפש: `Gmail API`
3. לחץ על "Gmail API"
4. לחץ "Enable"

### שלב 3️⃣: הגדרת OAuth Consent Screen

1. לך ל-**APIs & Services** → **OAuth consent screen**
2. בחר **External** (או Internal אם אתה ב-Google Workspace)
3. לחץ "Create"
4. מלא את הפרטים:
   - **App name**: Zero Agent
   - **User support email**: הדוא"ל שלך
   - **Developer contact**: הדוא"ל שלך
5. לחץ "Save and Continue"

### שלב 4️⃣: יצירת Credentials

1. לך ל-**APIs & Services** → **Credentials**
2. לחץ **"+ CREATE CREDENTIALS"** למעלה
3. בחר **OAuth client ID**
4. בחר **Desktop app** (או Web app)
5. תן שם: `Zero Gmail Client`
6. לחץ "Create"
7. **הורד את הקובץ JSON** כפתור "Download"
8. שנה את השם ל: `credentials.json`

### שלב 5️⃣: התקנת הקובץ

1. העתק את `credentials.json` ל:
   ```
   C:\AI-ALL-PRO\ZERO\credentials.json
   ```

### שלב 6️⃣: בדיקה

1. הפעל מחדש את השרת:
   ```powershell
   python api_server.py
   ```

2. בממשק האינטרנט:
   - לך לטאב **📧 אימייל**
   - לחץ "🔄 טען אימיילים"

3. בפעם הראשונה, תפתח דפדפן להרשאה:
   - אישר את ההרשאה
   - נכון נוצר קובץ `token.json`

## 🎯 מה קורה אחר כך?

לאחר ההרשאה:
- האימיילים יטענו אוטומטית
- תוכל לראות עד 10 אימיילים אחרונים
- התחברות תישמר ב-`token.json`

## ⚠️ הערות חשובות

### אם אתה מקבל שגיאה:
```
Error 403: access_denied
```

**פתרון**:
1. לך ל-**OAuth consent screen**
2. לחץ **"PUBLISH APP"**
3. לחץ "Confirm" (אפילו אם עדיין ב-Draft)

### אם אתה מקבל:
```
Invalid client
```

**פתרון**:
- ודא שהורדת את הקובץ הנכון
- ודא שהשם הוא בדיוק `credentials.json`

## 📱 מבנה התיקייה הסופי

```
C:\AI-ALL-PRO\ZERO\
├── credentials.json       ← הורד מ-Google Console
├── token.json            ← נוצר אוטומטית אחרי הרשאה
├── api_server.py
├── zero_web_interface.html
└── ...
```

## 🚀 אחרי ההתקנה

הממשק יעבוד עם:
- ✅ טעינת אימיילים
- ✅ חיפוש באימיילים
- ✅ שליחת אימיילים
- ✅ תצוגת אימיילים אחרונים

## 📞 עזרה נוספת

אם יש בעיות:
1. בדוק את ה-Console בדפדפן (F12)
2. בדוק את הלוגים של השרת
3. ודא שה-API מופעל ב-Google Console

**בהצלחה!** 🎉
