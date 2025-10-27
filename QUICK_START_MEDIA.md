# 🚀 Zero Agent - Quick Start for Media Generation

## ⚠️ **חשוב! הפעל את השרתים תחילה**

לפני שתוכל להשתמש ביצירת תמונות, סרטונים ודיבור, **חייב להפעיל** את שרתי המדיה!

---

## 📋 **הפעלה בשני שלבים:**

### **שלב 1️⃣: הפעל את שרתי המדיה**

**אופציה A - סקריפט אוטומטי (מומלץ):**
```powershell
cd C:\AI-ALL-PRO\ZERO
.\start_media_services.ps1
```

**אופציה B - ידני:**
```powershell
cd C:\AI-MEDIA-RTX5090\services
.\start-stack.ps1
```

**⏱️ המתן 30-60 שניות** לאתחול השרתים

---

### **שלב 2️⃣: בדוק שהשרתים פועלים**

פתח דפדפן ובדוק:

✅ **FLUX (תמונות):**
```
http://localhost:9188
```
אמור להציג את ממשק ComfyUI

✅ **CogVideoX (סרטונים):**
```
http://localhost:9056/health
```
אמור להחזיר: `{"status":"healthy"}`

✅ **HunyuanVideo:**
```
http://localhost:9055/health
```
אמור להחזיר: `{"status":"healthy"}`

✅ **Hebrew TTS:**
```
http://localhost:9033/health
```
אמור להחזיר: `{"status":"healthy"}`

---

## 🎮 **עכשיו אפשר להשתמש!**

פתח את Zero Agent: http://localhost:8080/simple

### **דוגמאות לפקודות:**

#### **🎨 יצירת תמונות:**
```
צור תמונה של דג סלמון בנורווגיה
generate image of a sunset over mountains
צייר נוף הררי עם אגם
```

#### **🎥 יצירת סרטונים:**
```
צור סרטון של חתול מנגן בפסנתר
create video of waves crashing on beach
הפק סרטון של רקדן ברחוב
```

#### **🗣️ דיבור בעברית:**
```
הקרא בקול: שלום עולם, אני Zero
דבר: ברוכים הבאים למערכת Zero Agent
speak: Welcome to the future
```

---

## ❌ **פתרון בעיות**

### **בעיה: "Service is not running"**

**פתרון:**
1. וודא שהפעלת את השרתים (שלב 1)
2. המתן 30-60 שניות
3. בדוק שהשרתים פועלים (שלב 2)
4. אם עדיין לא עובד:
```powershell
cd C:\AI-MEDIA-RTX5090\services
.\stop-stack.ps1
.\start-stack.ps1
```

### **בעיה: "Connection refused"**

**פתרון:**
```powershell
# בדוק אם השרתים רצים:
docker ps

# אם לא - הפעל מחדש:
cd C:\AI-MEDIA-RTX5090\services
.\start-stack.ps1
```

### **בעיה: "Out of VRAM"**

**פתרון:**
- סגור אפליקציות GPU אחרות
- השתמש רק ב-**שירות אחד** בכל פעם (video)
- הפעל מחדש Docker:
```powershell
docker restart rtx5090-cogvideo
```

---

## 📊 **מצב השרתים**

בדוק סטטוס של כל השרתים:
```powershell
cd C:\AI-MEDIA-RTX5090\services
.\status-check.ps1
```

---

## 🎯 **טיפים מקצועיים**

1. **הפעל את השרתים פעם אחת** בבוקר - הם ממשיכים לרוץ עד שתכבה את המחשב

2. **כתוב prompts טובים:**
   ```
   ✅ טוב: "A photorealistic salmon fish swimming in Norwegian fjords, clear water, mountains, golden hour"
   ❌ פחות טוב: "fish"
   ```

3. **התאזר בסבלנות:**
   - תמונות: 3-8 שניות ⚡
   - סרטונים: 45-180 שניות ⏳
   - דיבור: 1-3 שניות ⚡

4. **שמור את התוצאות:**
   - תמונות: `ZERO/generated/images/`
   - סרטונים: `ZERO/generated/videos/`
   - אודיו: `ZERO/generated/audio/`

---

## 🆘 **עזרה נוספת**

- **מדריך מלא:** `MEDIA_GENERATION_GUIDE.md`
- **תיעוד טכני:** `C:\AI-MEDIA-RTX5090\services\README.md`
- **לוגים:** `C:\AI-MEDIA-RTX5090\logs\`

---

**🎉 הצלחה! תהנה מיצירה עם AI!**

