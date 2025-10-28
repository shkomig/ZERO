# פתרון בעיות TTS (Text-to-Speech)

## 🔊 **הבעיה: "לא תמיד מקבל קול"**

### **סיבות אפשריות:**

---

## 1️⃣ **שירות TTS לא רץ**

### **בדיקה:**
```bash
# בדוק אם השירות רץ:
curl http://localhost:5003/health
```

**אם לא עובד:**
```bash
# בטרמינל נפרד, הפעל:
cd C:\AI-MEDIA-RTX5090\tts-hebrew-service
python app.py
```

---

## 2️⃣ **פורמט הפקודה לא נכון**

### **פורמטים שעובדים:**
```
✅ הקרא בקול: שלום עולם
✅ הקרא בקול שלום עולם
✅ דבר: שלום עולם
✅ תדבר: שלום עולם
```

### **פורמטים שלא עובדים:**
```
❌ הקרא "שלום עולם" בקול
❌ שלום עולם (בלי "הקרא בקול")
❌ תגיד שלום (השירות מחפש "הקרא בקול" או "דבר")
```

---

## 3️⃣ **הקובץ נוצר אבל לא מתנגן**

### **בדיקה:**
```bash
# בדוק אם יש קבצי אודיו:
dir C:\AI-ALL-PRO\ZERO\generated\audio\
```

**אם יש קבצים אבל לא נשמע:**
- נסה לפתוח קובץ ידנית: `Invoke-Item C:\AI-ALL-PRO\ZERO\generated\audio\tts_hebrew_*.wav`
- בדוק עוצמת קול במחשב
- בדוק הגדרות נגן ברירת מחדל

---

## 4️⃣ **הפקודה לא מזוהה**

### **בעיה:** Computer Control לא מזהה את הפקודה

**תיקון:**
בדוק ב-`nlp_parser.py` שהפקודות מוגדרות:

```python
self.hebrew_patterns = {
    "speak": [
        r"הקרא בקול:?\s*(.+)",
        r"תקרא בקול:?\s*(.+)",
        r"דבר:?\s*(.+)",
        r"תדבר:?\s*(.+)"
    ]
}
```

---

## 🧪 **בדיקות מומלצות:**

### **בדיקה 1: שירות TTS**
```bash
curl -X GET "http://localhost:5003/tts?text=שלום"
```
**צפוי:** קובץ WAV יתקבל

### **בדיקה 2: פקודה דרך Zero**
בממשק Zero:
```
הקרא בקול: בדיקה אחת שתיים שלוש
```
**צפוי:** קול מתנגן אוטומטית

### **בדיקה 3: קבצים שנשמרו**
```powershell
Get-ChildItem C:\AI-ALL-PRO\ZERO\generated\audio\ -Filter "*.wav" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

---

## 🔧 **תיקונים נפוצים:**

### **תיקון 1: נקה קבצים ישנים**
```powershell
Remove-Item C:\AI-ALL-PRO\ZERO\generated\audio\tts_hebrew_*.wav
```

### **תיקון 2: וודא שתקיית generated קיימת**
```powershell
New-Item -ItemType Directory -Force -Path C:\AI-ALL-PRO\ZERO\generated\audio
```

### **תיקון 3: בדוק הרשאות**
```powershell
# ודא שיש הרשאות כתיבה:
Test-Path C:\AI-ALL-PRO\ZERO\generated\audio -PathType Container
```

---

## 📋 **לוג בדיקות:**

רשום כאן את הבדיקות שלך:

### **בדיקה מס' 1:**
```
פקודה: הקרא בקול: שלום
תוצאה: □ עבד  □ לא עבד
שגיאה (אם יש): _________________
```

### **בדיקה מס' 2:**
```
פקודה: דבר: ברוכים הבאים
תוצאה: □ עבד  □ לא עבד
שגיאה (אם יש): _________________
```

### **בדיקה מס' 3:**
```
פקודה: תדבר: אני זירו
תוצאה: □ עבד  □ לא עבד
שגיאה (אם יש): _________________
```

---

## 💡 **טיפים:**

1. **פקודה אחת בכל פעם** - אל תשלח הרבה פקודות TTS ברצף מהיר
2. **המתן לסיום** - תן לקול להסתיים לפני שאתה שולח פקודה נוספת
3. **בדוק לוגים** - הלוגים יראו אם השירות מגיב:
   ```
   INFO:zero_agent.tools.tool_tts_hebrew:🗣️ Generating speech: שלום...
   INFO:zero_agent.tools.tool_tts_hebrew:✅ Audio saved: ZERO\generated\audio\tts_hebrew_1761594483.wav
   INFO:zero_agent.tools.computer_control_agent:🔊 Playing audio: ...
   ```

---

## 🚀 **בדיקה מהירה - 3 צעדים:**

### **צעד 1: בדוק שירות**
```bash
curl http://localhost:5003/health
```
**תוצאה צפויה:** `{"status": "ok"}`

### **צעד 2: שלח פקודה**
בממשק Zero:
```
הקרא בקול: בדיקה
```

### **צעד 3: בדוק לוגים**
חפש בטרמינל:
```
🗣️ Generating speech
✅ Audio saved
🔊 Playing audio
```

**אם כל 3 הצעדים עברו - הכל תקין!** ✅

**אם לא - תראה איזה צעד נכשל ותדווח.** 📝

---

## 📞 **זקוק לעזרה?**

אם עדיין לא עובד, שלח את המידע הבא:
1. לוגים מהטרמינל (החלק עם TTS)
2. תוצאת `curl http://localhost:5003/health`
3. רשימת קבצים ב-`generated/audio/`
4. הפקודה המדויקת ששלחת

**אני אעזור לך לפתור!** 🔧



