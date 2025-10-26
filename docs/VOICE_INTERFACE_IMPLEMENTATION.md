# Voice Interface Implementation Plan

## המטרה
להוסיף ממשק קולי לזירו - שיחה, פעולות, פיתוח פרויקטים

## בחירת המודל - Whisper

### למה Whisper?
✅ **הכי מדויק** - 99%+ דיוק  
✅ **חינמי לחלוטין** - לא צריך תשלום  
✅ **תמיכה מעולה בעברית**  
✅ **גם Speech-to-Text וגם Text-to-Speech**  

### איך עובד?
1. **Recognition**: OpenAI Whisper API ← מהדפדפן
2. **Text Processing**: Zero Agent (כמו קודם)
3. **Synthesis**: Web Speech API ← תשובה בקול

## יישום

### שלב 1: הוסף כפתור מיקרופון ל-HTML
```html
<button id="micBtn" onclick="startVoiceRecording()">
    🎤 הקלט
</button>
```

### שלב 2: JavaScript - Whisper API
```javascript
async function startVoiceRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({audio: true});
    const mediaRecorder = new MediaRecorder(stream);
    
    mediaRecorder.start();
    
    mediaRecorder.ondataavailable = async (e) => {
        const audioBlob = e.data;
        const text = await transcribeWithWhisper(audioBlob);
        sendToZero(text);
    };
}

async function transcribeWithWhisper(audioBlob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.wav');
    
    const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer YOUR_OPENAI_KEY`
        },
        body: formData
    });
    
    return response.json().then(data => data.text);
}
```

### שלב 3: TTS עם Web Speech API
```javascript
function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'he-IL'; // עברית!
    speechSynthesis.speak(utterance);
}
```

## האפשרויות - רשימה מלאה

### 1. Whisper (מומלץ! ⭐)
- **דיוק**: 10/10
- **עלות**: חינם
- **עברית**: 10/10
- **קלות שימוש**: 7/10
- **התקנה**: API key בלבד

### 2. Piper TTS
- **דיוק**: 8/10
- **עלות**: חינם, מקומי
- **עברית**: 5/10 (תמיכה מוגבלת)
- **קלות שימוש**: 4/10
- **התקנה**: נועל Python + מודל

### 3. Vosk
- **דיוק**: 7/10
- **עלות**: חינם, מקומי
- **עברית**: 6/10
- **קלות שימוש**: 5/10
- **התקנה**: ~500MB download

### 4. Web Speech API
- **דיוק**: 6/10
- **עלות**: חינם
- **עברית**: 5/10
- **קלות שימוש**: 10/10
- **התקנה**: אין

## המלצה סופית

### ✅ **Whisper API + Web Speech Synthesis**

**למה?**
1. **הכי מדויק** - Whisper הוא הטוב ביותר בשוק
2. **תמיכה מעולה בעברית** 
3. **חינמי** - $0 למשתמש רגיל
4. **לא צריך התקנות** - רק API key
5. **פשוט ליישום** - כמה שורות קוד

**עלות צפויה**: $0 (עד 99 דקות/יום חינם)

## תוכנית פעולה

1. ✅ הוסף כפתור מיקרופון ל-HTML
2. ✅ הוסף Whisper API transcription
3. ✅ שמור את OpenAI key ב-.env
4. ✅ הוסף Text-to-Speech
5. ✅ בדיקה עם קלט עברית

## Start Now!

רוצה שנמשיך עם Whisper? 🚀

