# 🎯 **תוכנית עבודה: שיפור Zero Agent**

**תאריך:** 28 אוקטובר 2025  
**סטטוס:** בביצוע

---

## 📋 **3 משימות עיקריות**

---

## **משימה 1: שיפור מבנה תשובות**

### 🎯 **מטרה**
Zero יחזיר תשובות מובנות עם:
- כותרות וכותרות משנה
- רשימות ממוספרות/תבליטים
- חלוקה לנושאים
- עיצוב נקי וקריא

### 📚 **מחקר - מה גילינו**
1. **הגדרת מבנה קבוע**: פורמט אחיד לכל התשובות
2. **שימוש במתווה מפורט**: תכנון מבנה לפני כתיבה
3. **הוספת דוגמאות**: הסברים מפורטים תחת כל נושא

### 🔧 **פתרון מוצע**

#### **שלב 1: הוסף דוגמאות למבנה מסודר ב-System Prompt**
```python
# api_server.py - System Prompt Enhancement
preferences = """אתה Zero Agent, עוזר AI חכם. ענה בעברית.

חוקי עיצוב תשובות:
1. תשובות קצרות → ישיר לעניין
2. תשובות מורכבות → מבנה מסודר:
   - כותרות: **כותרת**
   - רשימות: 1. פריט ראשון
   - קוד: ```python ... ```

דוגמאות מבנה טוב:
שאלה: "הסבר לי על Python"
תשובה:
**Python - שפת תכנות רב-תכליתית**

**מה זה Python?**
שפת תכנות קלה ללמידה, פופולרית לפיתוח אפליקציות.

**שימושים עיקריים:**
1. פיתוח אתרים (Django, Flask)
2. ניתוח נתונים (Pandas, NumPy)
3. בינה מלאכותית (TensorFlow, PyTorch)

**דוגמה:**
```python
print("Hello, World!")
```
"""
```

#### **שלב 2: הוסף Post-Processing לעיצוב**
```python
def format_response(response: str) -> str:
    """
    Format response with better structure
    """
    # Add markdown headers for key sections
    keywords_for_headers = ["מה זה", "למה", "איך", "דוגמה", "שימושים"]
    
    lines = response.split('\n')
    formatted = []
    
    for line in lines:
        # Check if line should be a header
        if any(kw in line for kw in keywords_for_headers):
            formatted.append(f"**{line.strip()}**")
        else:
            formatted.append(line)
    
    return '\n'.join(formatted)
```

#### **שלב 3: בדיקות**
- ✅ שאלות פשוטות → תשובות קצרות
- ✅ שאלות מורכבות → מבנה מסודר
- ✅ בקשות קוד → קוד עם הסברים

---

## **משימה 2 + 3: תיקון בעיית החזרת קוד**

### 🔍 **תוצאות בדיקה**

| Test | Input | Has Code? | Status |
|------|-------|-----------|--------|
| 1 | "תן לי קוד Python למשחק פשוט" | ✅ יש קוד | OK |
| 2 | "כתוב לי קוד Python להדפסת Hello World" | ❌ אין קוד | FAIL |
| 3 | "תבנה לי פונקציה Python לחישוב סכום" | ✅ יש קוד | OK |

### ❌ **הבעיה**
Test 2 החזיר **41 תווים בלבד** - תשובה קצרה מדי, ללא קוד.

### 🔍 **ניתוח**
1. **אפשרות 1**: Router בחר מודל לא נכון (mistral במקום coder)
2. **אפשרות 2**: המודל החזיר תשובה חלקית
3. **אפשרות 3**: בעיית encoding (הבדיקה נכשלה בהדפסה)

### 🔧 **פתרון**

#### **שלב 1: שפר זיהוי בקשות קוד ב-Router**
```python
# model_router.py
code_action_words = [
    "תבנה", "צור", "כתוב", "בנה", "פתח", "קוד",
    "כתוב לי קוד", "תן לי קוד",  # NEW!
    "write code", "build app", "create", "implement"
]
```

#### **שלב 2: הוסף Prompt Enforcement לקוד**
```python
# api_server.py - בבדיקת מודל coder
if model == "coder":
    prompt += "\n**חשוב: החזר קוד מלא עם הסברים!**\n"
```

#### **שלב 3: בדוק היסטוריית שיחות בווב**
נבדוק את השיחות האחרונות בממשק:
1. פתח את זכרון המערכת (`memory/short_term_memory.py`)
2. חפש את השיחות האחרונות
3. נתח מה המודל החזיר

---

## **משימה 4 (BONUS): שיחת קול מלאה**

### 🎯 **מטרה**
- אני מדבר → Zero שומע
- Zero עונה → אני שומע (לא רואה טקסט)
- כמו GPT Voice

### 📚 **מחקר מהמסמך המצורף**

מהקובץ `ניהול שיחה עם סוכן.md`:

#### **מודלים בקוד פתוח:**
| שם מודל | יתרונות | חסרונות |
|---------|----------|----------|
| SpeechT5 | קוד פתוח, תמיכה בקולות מגוונים | דורש משאבים |
| GPT-OSS | פריסה מקומית, פרטיות | דרוש ידע בתפעול |
| Whisper | דיוק טוב, תמיכה ב-100+ שפות | בעיקר טקסט |

#### **אסטרטגיה מומלצת:**
1. **Speech-to-Text (STT):** Whisper (OpenAI)
2. **Text-to-Speech (TTS):** 
   - שירות מקומי קיים (port 5002)
   - אלטרנטיבה: Google TTS, Amazon Polly
3. **אינטגרציה:** LiveKit / WebRTC לזרימה בזמן אמת

### 🔧 **פתרון מוצע**

#### **שלב 1: תקן את שירות ה-TTS הקיים**
```python
# Current status: TTS service on port 5002 is NOT running
# Solution: Start Hebrew TTS service or integrate alternative
```

#### **שלב 2: שפר Voice Input (VAD)**
```javascript
// zero_chat_simple.html
// Current: Manual button press
// Target: Auto-detect voice activity

let vadActive = false;
let silenceTimer = null;

function startVAD() {
    vadActive = true;
    recognition.start();
    
    // Auto-stop after 2 seconds of silence
    recognition.onresult = (event) => {
        clearTimeout(silenceTimer);
        silenceTimer = setTimeout(() => {
            stopRecordingAndSend();
        }, 2000);
    };
}
```

#### **שלב 3: Voice Output Automation**
```javascript
// zero_chat_simple.html
// Auto-play TTS when response arrives

async function handleVoiceResponse(text) {
    try {
        const audioUrl = `/api/tts?text=${encodeURIComponent(text)}`;
        const audio = new Audio(audioUrl);
        await audio.play();
        
        // Hide text display (voice-only mode)
        if (voiceOnlyMode) {
            // Don't show text, just play audio
        }
    } catch (error) {
        console.error('[Voice] TTS failed:', error);
    }
}
```

#### **שלב 4: Voice-Only Mode**
```html
<!-- Add toggle button -->
<button class="voice-mode-btn" onclick="toggleVoiceMode()">
    🎤 מצב קול בלבד
</button>
```

```javascript
let voiceOnlyMode = false;

function toggleVoiceMode() {
    voiceOnlyMode = !voiceOnlyMode;
    
    if (voiceOnlyMode) {
        // Hide chat history, show only mic
        document.querySelector('.chat-box').style.display = 'none';
        document.querySelector('.mic-btn').style.fontSize = '48px';
        startVAD(); // Auto-start listening
    } else {
        // Show chat history
        document.querySelector('.chat-box').style.display = 'block';
    }
}
```

---

## 📊 **סדר ביצוע מומלץ**

### **Priority 1: תיקון בעיית הקוד (משימה 2+3)**
⏱️ זמן: 30 דקות
```
1. שפר Router - זיהוי "תן לי קוד", "כתוב לי קוד"
2. הוסף Prompt Enforcement לקוד
3. בדיקות נוספות
4. בדוק היסטוריית שיחות בווב
```

### **Priority 2: שיפור מבנה תשובות (משימה 1)**
⏱️ זמן: 45 דקות
```
1. עדכן System Prompt עם דוגמאות מבנה
2. הוסף Post-Processing (אופציונלי)
3. בדיקות עם שאלות מורכבות
```

### **Priority 3: שיחת קול מלאה (משימה 4 - BONUS)**
⏱️ זמן: 2-3 שעות
```
1. תקן TTS service (port 5002)
2. שפר Voice Input (VAD auto-detect)
3. Voice Output Automation
4. Voice-Only Mode
5. בדיקות מקיפות
```

---

## ✅ **סטטוס נוכחי**

- ✅ Router חכם מותקן ועובד
- ✅ qwen2.5-coder מותקן למשימות קוד
- ✅ mistral מותקן להסברים עבריים
- ⚠️ בעיה: לפעמים לא מחזיר קוד (תשובות קצרות)
- ⚠️ מבנה תשובות: לא תמיד מסודר
- ❌ TTS service: לא רץ (port 5002)
- ⚠️ Voice Input: עובד אבל לא אוטומטי

---

## 🎯 **מה עושים עכשיו?**

אני מציע להתחיל ב-**Priority 1** (תיקון בעיית הקוד), ואז **Priority 2** (מבנה תשובות).

**BONUS (Priority 3)** זה פרויקט גדול יותר שדורש:
- תיקון/החלפת שירות TTS
- שיפור ממשק הקול
- בדיקות מקיפות

---

**אתה מוכן שנתחיל?** 🚀




