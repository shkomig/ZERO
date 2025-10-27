# 🎨 Zero Agent - Media Generation Guide
**AI-Powered Image, Video & Voice Generation**

---

## ✨ **מה חדש?**

Zero Agent עכשיו משולב עם RTX 5090 Media Stack שלך!

### **שירותים זמינים:**

| שירות | מה זה עושה | זמן יצירה | VRAM |
|------|------------|-----------|------|
| 🎨 **FLUX.1-schnell** | יצירת תמונות | 3-8 שניות | 6-8GB |
| 🎥 **CogVideoX-5B** | יצירת סרטונים | 45-120 שניות | 18-22GB |
| 🎬 **HunyuanVideo** | תמונה לסרטון | 60-180 שניות | 20-24GB |
| 🗣️ **Hebrew TTS** | דיבור בעברית | 1-3 שניות | <2GB |

---

## 🚀 **איך להשתמש?**

### **1. 🎨 יצירת תמונות (FLUX)**

פשוט תכתוב מה אתה רוצה וZero יצור את התמונה!

#### **דוגמאות בעברית:**
```
צור תמונה של דג סלמון בנורווגיה
תצור תמונה של חתול חמוד עם כובע
צייר נוף הררי בשקיעה
הפק תמונה של רובוט עתידני
```

#### **דוגמאות באנגלית:**
```
generate image of a salmon fish in Norwegian fjords
create image of a cyberpunk city at night
draw a mountain landscape at sunset
make image of a futuristic robot
```

#### **פרמטרים מתקדמים (אופציונלי):**
```python
# דרך פקודה ישירה (עבור מתכנתים):
from zero_agent.tools.tool_image_generation import image_tool

result = image_tool.generate_image(
    prompt="A majestic eagle soaring over mountains",
    width=1024,
    height=1024,
    steps=4,  # 4-8 for FLUX schnell
    seed=42   # For reproducible results
)
```

**תוצאה:**
- התמונה מתחילה להיווצר מיד
- צפה בתהליך ב-ComfyUI: http://localhost:9188
- התמונה נשמרת אוטומטית

---

### **2. 🎥 יצירת סרטונים (CogVideoX)**

יצירת סרטונים מטקסט!

#### **דוגמאות בעברית:**
```
צור סרטון של חתול מנגן בפסנתר
תצור סרטון של גלים מתנפצים על חוף
הפק סרטון של רקדן ברחוב
צור וידאו של מכונית עתידנית
```

#### **דוגמאות באנגלית:**
```
generate video of a cat playing piano in a jazz club
create video of waves crashing on a beach
make video of a dancer performing in the street
render video of a futuristic car driving
```

#### **פרמטרים מתקדמים:**
```python
from zero_agent.tools.tool_video_generation import video_tool

result = video_tool.generate_video_cogvideo(
    prompt="A cat playing piano in a jazz club",
    num_frames=49,    # 9-49 frames
    height=480,       # 256-720
    width=848,        # 256-1280
    steps=50,         # 10-50
    guidance=6.0,     # 1.0-20.0
    seed=42
)
```

**⏱️ זמן יצירה:** 45-120 שניות (תלוי במורכבות)

**הורדת הסרטון:**
```
http://localhost:9056/download/cogvideo_42.mp4
```

---

### **3. 🎬 תמונה לסרטון (HunyuanVideo)**

הפוך תמונה לסרטון!

#### **שימוש:**
```
צור סרטון מהתמונה של החתול
```

#### **API מתקדם:**
```python
result = video_tool.generate_video_hunyuan(
    prompt="A cat moving its head and purring",
    image_path="/path/to/cat.jpg",  # Image to animate
    num_frames=49,
    height=480,
    width=848,
    steps=30,
    seed=42
)
```

**⏱️ זמן יצירה:** 60-180 שניות

---

### **4. 🗣️ דיבור בעברית (Hebrew TTS)**

Zero יכול לקרוא כל טקסט בקול!

#### **דוגמאות:**
```
הקרא בקול: שלום עולם, אני Zero
דבר: ברוכים הבאים למערכת Zero Agent
תהגה: זוהי הדגמה של מערכת דיבור בעברית
```

#### **אנגלית:**
```
speak: Hello world, I am Zero
say: Welcome to Zero Agent
read aloud: This is a demonstration
```

#### **API ישיר:**
```python
from zero_agent.tools.tool_tts_hebrew import tts_tool

result = tts_tool.text_to_speech(
    text="שלום עולם, אני Zero, עוזר הבינה המלאכותית שלך",
    save_to_file=True
)

# הקובץ נשמר ב:
# ZERO/generated/audio/tts_hebrew_<timestamp>.wav
```

**⚠️ רישיון:** CC-BY-NC 4.0 (שימוש לא מסחרי בלבד!)

---

## 📊 **סטטוס שירותים**

### בדיקת זמינות:
```bash
# FLUX (Image)
curl http://localhost:9188/

# CogVideoX (Video)
curl http://localhost:9056/health

# HunyuanVideo (I2V)
curl http://localhost:9055/health

# Hebrew TTS
curl http://localhost:9033/health
```

### אם שירות לא עובד:
```powershell
cd C:\AI-MEDIA-RTX5090\services
.\start-stack.ps1
```

---

## 🎯 **דוגמאות מלאות**

### **דוגמה 1: זרימת עבודה מלאה**
```
1. User: צור תמונה של חתול חמוד
   Zero: ✅ Image generation started: flux_12345

2. User: צור סרטון של החתול הזה
   Zero: ✅ Video generation started: cogvideo_67890.mp4

3. User: הקרא בקול: החתול חמוד מאוד
   Zero: ✅ Speech generated: tts_hebrew_111222.wav
```

### **דוגמה 2: אוטומציה מלאה**
```python
# Script שיוצר פרזנטציה אוטומטית

from zero_agent.tools import image_tool, video_tool, tts_tool

# 1. צור תמונת כותרת
title_image = image_tool.generate_simple("Professional title slide: Zero Agent Presentation")

# 2. צור סרטון הדגמה
demo_video = video_tool.generate_simple("Product demonstration animation", service="cogvideo")

# 3. צור קריינות
narration = tts_tool.speak_simple("ברוכים הבאים להצגת Zero Agent, מערכת הבינה המלאכותית המתקדמת")

print(f"Created: {title_image}, {demo_video}, {narration}")
```

---

## 📂 **מבנה קבצים**

כל הפלטים נשמרים ב:

```
ZERO/
  generated/
    images/          # תמונות מ-FLUX
    videos/          # סרטונים מ-CogVideoX/HunyuanVideo
    audio/           # קבצי אודיו מ-TTS
```

---

## ⚙️ **הגדרות מתקדמות**

### **תקלות ופתרונות:**

#### **בעיה: "Service not running"**
```powershell
# הפעל את ה-Stack:
cd C:\AI-MEDIA-RTX5090\services
.\start-stack.ps1

# בדוק סטטוס:
.\status-check.ps1
```

#### **בעיה: "Out of VRAM"**
- רוץ רק **שירות אחד** בכל פעם (video)
- סגור אפליקציות GPU אחרות
- השתמש ב-FP8 models (כבר מוגדר)

#### **בעיה: "Generation timeout"**
- הקטן את מספר ה-frames
- הקטן את ה-resolution
- הקטן את מספר ה-steps

---

## 🔧 **API מתקדם**

### **Image Generation API**
```python
from zero_agent.tools.tool_image_generation import image_tool

# Basic
result = image_tool.generate_simple("A beautiful sunset")

# Advanced
result = image_tool.generate_image(
    prompt="A majestic eagle flying",
    negative_prompt="blurry, low quality",
    width=1024,
    height=1024,
    steps=4,
    seed=42
)

if result["success"]:
    print(f"Image: {result['prompt_id']}")
else:
    print(f"Error: {result['error']}")
```

### **Video Generation API**
```python
from zero_agent.tools.tool_video_generation import video_tool

# CogVideoX
result = video_tool.generate_video_cogvideo(
    prompt="Waves on beach",
    num_frames=49,
    steps=50,
    seed=42
)

# HunyuanVideo (Image-to-Video)
result = video_tool.generate_video_hunyuan(
    prompt="Moving clouds",
    image_path="/path/to/image.jpg",
    num_frames=49,
    steps=30
)

print(f"Video: {result['download_url']}")
```

### **TTS API**
```python
from zero_agent.tools.tool_tts_hebrew import tts_tool

result = tts_tool.text_to_speech(
    text="שלום עולם",
    save_to_file=True
)

print(f"Audio saved: {result['filepath']}")
```

---

## 📊 **טבלת השוואה**

| Feature | FLUX | CogVideoX | HunyuanVideo | Hebrew TTS |
|---------|------|-----------|--------------|------------|
| **Input** | Text | Text | Text + Image | Text |
| **Output** | Image | Video | Video | Audio |
| **Resolution** | Up to 1024x1024 | Up to 720p | Up to 720p | WAV |
| **Speed** | 3-8s | 45-120s | 60-180s | 1-3s |
| **VRAM** | 6-8GB | 18-22GB | 20-24GB | <2GB |
| **Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **License** | Apache 2.0 | Apache 2.0 | Apache 2.0 | CC-BY-NC 4.0 |

---

## 🎓 **עצות שימוש**

### **כתיבת Prompts טובים:**

✅ **טוב:**
```
A photorealistic salmon fish swimming in Norwegian fjords, 
clear water, mountains in background, golden hour lighting
```

❌ **פחות טוב:**
```
fish
```

### **אופטימיזציה:**

1. **Image Generation:**
   - השתמש ב-4 steps ל-FLUX schnell (מהיר)
   - רזולוציה 1024x1024 מאוזנת
   - Seed קבוע לתוצאות זהות

2. **Video Generation:**
   - התחל עם 49 frames (איכות/מהירות מאוזנת)
   - השתמש ב-guidance scale 6.0 (ברירת מחדל)
   - רק שירות אחד בכל פעם (VRAM)

3. **TTS:**
   - טקסט קצר (<100 מילים) לתוצאות טובות
   - עברית תקנית עובדת הכי טוב
   - שמור קבצים לשימוש חוזר

---

## 🔒 **רישוי ואבטחה**

### **רישיונות:**
- **FLUX.1 schnell**: Apache 2.0 ✅ (שימוש מסחרי OK)
- **CogVideoX-5B**: Apache 2.0 ✅ (שימוש מסחרי OK)
- **HunyuanVideo**: Apache 2.0 ✅ (שימוש מסחרי OK)
- **Hebrew TTS**: CC-BY-NC 4.0 ⚠️ (**שימוש לא מסחרי בלבד!**)

### **פרטיות:**
- כל הפעולות **מקומיות** (RTX 5090)
- **אין העלאה לענן**
- **אין שמירת נתונים חיצונית**
- **100% פרטי ומאובטח**

---

## 🆘 **תמיכה**

### **בעיות נפוצות:**

**Q: הפקודה לא מזוהה?**
A: וודא שהתחלת עם:
- `צור תמונה של...` (לא רק "תמונה של")
- `צור סרטון של...`
- `הקרא בקול: ...`

**Q: השירות לא זמין?**
A: הפעל את ה-Stack:
```powershell
cd C:\AI-MEDIA-RTX5090\services
.\start-stack.ps1
```

**Q: הזמן יצירה ארוך?**
A: זה נורמלי:
- תמונות: 3-8 שניות
- סרטונים: 45-180 שניות (תלוי במורכבות)

**Q: איכות נמוכה?**
A: הגדל:
- Steps (4→8 לתמונות, 30→50 לסרטונים)
- Resolution
- שפר את ה-prompt

---

## 📖 **קישורים שימושיים**

- **ComfyUI Interface**: http://localhost:9188
- **CogVideoX API**: http://localhost:9056/docs
- **HunyuanVideo API**: http://localhost:9055/docs
- **Hebrew TTS API**: http://localhost:9033/docs
- **Zero Agent Dashboard**: http://localhost:8080/simple

---

**נוצר על ידי:** Zero Agent Team  
**אופטימיזציה עבור:** NVIDIA RTX 5090  
**עודכן לאחרונה:** אוקטובר 2025  

🎉 **תהנה מיצירה עם AI!**

