# Phase 2: Real-Time Features - שיחה טבעית

## 🎯 **מטרה:**
להפוך את Zero לעוזר קולי **טבעי** שמרגיש כמו שיחה אמיתית!

---

## 🎭 **החזון:**

```
משתמש מתחיל לדבר → Zero מזהה אוטומטית
משתמש מפסיק לדבר → Zero עונה מיד
משתמש קוטע → Zero עוצר ומקשיב
```

**כמו שיחה עם אדם אמיתי!** 🗣️

---

## 📋 **4 תכונות עיקריות:**

### **1️⃣ Voice Activity Detection (VAD)**

**מה זה:**  
זיהוי אוטומטי מתי משתמש מדבר - **בלי ללחוץ כפתור!**

**טכנולוגיה:** `webrtcvad` (ספרייה של Google)

#### **התקנה:**
```bash
pip install webrtcvad
```

#### **קוד - Python (backend):**

```python
# zero_agent/tools/voice_activity_detector.py

import webrtcvad
import collections
import wave

class VoiceActivityDetector:
    """
    זיהוי פעילות קולית בזמן אמת
    """
    
    def __init__(self, aggressiveness=3):
        """
        Args:
            aggressiveness: 0-3 (3 = הכי רגיש)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = 16000
        self.frame_duration_ms = 30  # 30ms per frame
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000) * 2
        
    def is_speech(self, audio_frame: bytes) -> bool:
        """
        בדוק אם frame מכיל דיבור
        
        Args:
            audio_frame: Raw audio data (16kHz, 16-bit, mono)
            
        Returns:
            True אם יש דיבור, False אחרת
        """
        try:
            return self.vad.is_speech(audio_frame, self.sample_rate)
        except Exception as e:
            return False
    
    def detect_speech_segments(self, audio_frames: list) -> list:
        """
        מזהה התחלות וסיומים של דיבור
        
        Returns:
            רשימה של (start_frame, end_frame) tuples
        """
        speech_segments = []
        is_speaking = False
        segment_start = None
        
        for i, frame in enumerate(audio_frames):
            if self.is_speech(frame):
                if not is_speaking:
                    # התחלת דיבור
                    is_speaking = True
                    segment_start = i
            else:
                if is_speaking:
                    # סיום דיבור
                    is_speaking = False
                    speech_segments.append((segment_start, i))
        
        # אם הדיבור לא נגמר בסוף
        if is_speaking and segment_start is not None:
            speech_segments.append((segment_start, len(audio_frames)))
        
        return speech_segments


class SpeechSegmentDetector:
    """
    מזהה מתי להתחיל ולעצור הקלטה
    """
    
    def __init__(self, vad: VoiceActivityDetector):
        self.vad = vad
        self.buffer_size = 15  # מספר frames לבדוק
        self.speech_threshold = 0.6  # 60% של frames צריכים להיות דיבור
        self.silence_threshold = 0.3  # 30% שקט = סיום
        self.ring_buffer = collections.deque(maxlen=self.buffer_size)
        
    def process_frame(self, frame: bytes) -> str:
        """
        עבד frame ובדוק מצב
        
        Returns:
            "start" - התחל הקלטה
            "continue" - המשך הקלטה
            "stop" - עצור הקלטה
            "silence" - שקט
        """
        is_speech = self.vad.is_speech(frame)
        self.ring_buffer.append(is_speech)
        
        if len(self.ring_buffer) < self.buffer_size:
            return "silence"
        
        speech_ratio = sum(self.ring_buffer) / len(self.ring_buffer)
        
        if speech_ratio >= self.speech_threshold:
            return "start" if all(not x for x in list(self.ring_buffer)[:5]) else "continue"
        elif speech_ratio <= self.silence_threshold:
            return "stop"
        else:
            return "continue"
```

#### **קוד - JavaScript (frontend):**

```javascript
// zero_chat_simple.html - הוסף:

class VoiceActivityDetectorJS {
    constructor() {
        this.audioContext = null;
        this.analyser = null;
        this.silenceThreshold = -50; // dB
        this.silenceDuration = 1000; // 1 second
        this.lastSoundTime = Date.now();
        this.isSpeaking = false;
    }
    
    async initialize(stream) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.audioContext.createAnalyser();
        this.analyser.fftSize = 256;
        
        const source = this.audioContext.createMediaStreamSource(stream);
        source.connect(this.analyser);
    }
    
    getVolumeLevel() {
        const dataArray = new Uint8Array(this.analyser.frequencyBinCount);
        this.analyser.getByteFrequencyData(dataArray);
        
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        return 20 * Math.log10(average / 255); // Convert to dB
    }
    
    checkSpeech() {
        const volume = this.getVolumeLevel();
        const now = Date.now();
        
        if (volume > this.silenceThreshold) {
            // יש דיבור
            this.lastSoundTime = now;
            if (!this.isSpeaking) {
                this.isSpeaking = true;
                console.log("🎤 דיבור התחיל");
                this.onSpeechStart();
            }
        } else {
            // שקט
            if (this.isSpeaking && (now - this.lastSoundTime > this.silenceDuration)) {
                this.isSpeaking = false;
                console.log("🔇 דיבור נגמר");
                this.onSpeechEnd();
            }
        }
    }
    
    onSpeechStart() {
        // התחל הקלטה
        if (window.vadCallbacks && window.vadCallbacks.onStart) {
            window.vadCallbacks.onStart();
        }
    }
    
    onSpeechEnd() {
        // עצור והעבר לעיבוד
        if (window.vadCallbacks && window.vadCallbacks.onEnd) {
            window.vadCallbacks.onEnd();
        }
    }
    
    start() {
        this.checkInterval = setInterval(() => this.checkSpeech(), 100);
    }
    
    stop() {
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
        }
    }
}

// שימוש:
let vad = null;

async function enableAutoVAD() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    vad = new VoiceActivityDetectorJS();
    await vad.initialize(stream);
    
    window.vadCallbacks = {
        onStart: () => {
            console.log("מתחיל להקליט...");
            startRecording();
        },
        onEnd: () => {
            console.log("עוצר ושולח...");
            stopRecordingAndSend();
        }
    };
    
    vad.start();
    console.log("✅ VAD פעיל - דבר בחופשיות!");
}
```

**תוצאה:**
- ✅ אין צורך ללחוץ כפתור!
- ✅ Zero מזהה מתי אתה מדבר
- ✅ Zero עוצר הקלטה אוטומטית כשאתה שותק

---

### **2️⃣ Interrupt Handling**

**מה זה:**  
אם משתמש מתחיל לדבר תוך כדי תשובה - Zero **עוצר מיד**!

```python
# zero_agent/tools/interrupt_handler.py

import threading
import time

class InterruptHandler:
    """
    מטפל בהפרעות - עוצר תשובה אם משתמש מדבר
    """
    
    def __init__(self):
        self.is_responding = False
        self.should_interrupt = False
        self.current_response_thread = None
        self.lock = threading.Lock()
        
    def start_response(self):
        """מתחיל תשובה"""
        with self.lock:
            self.is_responding = True
            self.should_interrupt = False
    
    def request_interrupt(self):
        """מבקש עצירת תשובה"""
        with self.lock:
            if self.is_responding:
                self.should_interrupt = True
                print("⚠️ קיבלתי הפרעה - עוצר תשובה")
                return True
            return False
    
    def should_stop(self) -> bool:
        """בדוק אם צריך לעצור"""
        with self.lock:
            return self.should_interrupt
    
    def finish_response(self):
        """סיים תשובה"""
        with self.lock:
            self.is_responding = False
            self.should_interrupt = False


# שילוב עם streaming:
interrupt_handler = InterruptHandler()

def stream_response_with_interrupt(prompt):
    """Stream response עם אפשרות להפסיק"""
    interrupt_handler.start_response()
    
    try:
        for chunk in llm.stream_generate(prompt):
            # בדוק אם צריך לעצור
            if interrupt_handler.should_stop():
                print("⏹️ תשובה הופסקה")
                break
            
            yield chunk
            
    finally:
        interrupt_handler.finish_response()
```

**תוצאה:**
- ✅ משתמש יכול לקטוע בכל רגע
- ✅ Zero עוצר מיד (לא ממשיך לדבר)
- ✅ שיחה טבעית יותר!

---

### **3️⃣ Context-Aware Responses**

**מה זה:**  
Zero **זוכר** את ההקשר של השיחה ולא חוזר על עצמו!

```python
# zero_agent/tools/conversation_context.py

from datetime import datetime
from typing import List, Dict

class ConversationContext:
    """
    מנהל הקשר שיחה חכם
    """
    
    def __init__(self, max_turns=10):
        self.history: List[Dict] = []
        self.max_turns = max_turns
        self.current_topic = None
        self.user_preferences = {}
        
    def add_turn(self, user_input: str, agent_response: str):
        """הוסף תור לשיחה"""
        turn = {
            "user": user_input,
            "agent": agent_response,
            "timestamp": datetime.now(),
            "topic": self._detect_topic(user_input)
        }
        self.history.append(turn)
        
        # שמור רק X תורות אחרונים
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]
        
        # עדכן נושא נוכחי
        self.current_topic = turn["topic"]
    
    def _detect_topic(self, text: str) -> str:
        """זהה נושא השיחה"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["python", "קוד", "תכנות"]):
            return "programming"
        elif any(kw in text_lower for kw in ["מניה", "בורסה", "מסחר"]):
            return "trading"
        elif any(kw in text_lower for kw in ["מזג", "טמפרטורה"]):
            return "weather"
        else:
            return "general"
    
    def get_relevant_context(self, new_input: str, max_context=3) -> str:
        """החזר context רלוונטי בלבד"""
        new_topic = self._detect_topic(new_input)
        
        # אם זה אותו נושא - תן יותר הקשר
        if new_topic == self.current_topic:
            relevant_turns = self.history[-max_context:]
        else:
            # נושא חדש - רק התור האחרון
            relevant_turns = self.history[-1:] if self.history else []
        
        # בנה context string
        context_lines = []
        for turn in relevant_turns:
            context_lines.append(f"ש: {turn['user']}")
            context_lines.append(f"ת: {turn['agent']}")
        
        return "\n".join(context_lines) if context_lines else ""
    
    def is_follow_up(self, user_input: str) -> bool:
        """בדוק אם זו שאלת המשך"""
        if not self.history:
            return False
        
        follow_up_keywords = [
            "גם", "ועוד", "ומה על", "בנוסף",
            "also", "and", "what about", "how about"
        ]
        
        return any(kw in user_input.lower() for kw in follow_up_keywords)


# שימוש:
conversation = ConversationContext()

def get_response_with_context(user_input: str) -> str:
    """קבל תשובה עם הקשר"""
    
    # בנה prompt עם context
    context = conversation.get_relevant_context(user_input)
    
    if context:
        prompt = f"""
הקשר קודם:
{context}

שאלה חדשה:
ש: {user_input}
ת: 
"""
    else:
        prompt = f"ש: {user_input}\nת: "
    
    # קבל תשובה
    response = llm.generate(prompt)
    
    # שמור בהיסטוריה
    conversation.add_turn(user_input, response)
    
    return response
```

**תוצאה:**
- ✅ Zero זוכר את ההקשר
- ✅ לא צריך לחזור על עצמך
- ✅ שיחה זורמת!

---

### **4️⃣ Wake Word Detection**

**מה זה:**  
אמור **"זירו"** והוא מתחיל להקשיב!

```python
# zero_agent/tools/wake_word_detector.py

from pocketsphinx import LiveSpeech

class WakeWordDetector:
    """
    זיהוי מילת השכמה
    """
    
    def __init__(self, wake_word="zero"):
        self.wake_word = wake_word.lower()
        self.is_active = False
        
    def start_listening(self):
        """התחל להקשיב למילת השכמה"""
        print(f"🎧 מקשיב למילת השכמה: '{self.wake_word}'")
        
        # הגדר LiveSpeech
        speech = LiveSpeech(
            keyphrase=self.wake_word,
            kws_threshold=1e-20,
            audio_device=None
        )
        
        for phrase in speech:
            if self.wake_word in str(phrase).lower():
                print(f"🔔 זיהיתי '{self.wake_word}'!")
                self.on_wake_word_detected()
    
    def on_wake_word_detected(self):
        """קרה כשמילת השכמה מזוהה"""
        # הפעל הקלטה
        print("🎤 Zero מקשיב... דבר!")
        # כאן תוסיף קוד להתחלת הקלטה


# שימוש פשוט יותר - Web Speech API:
# בממשק HTML:
```

```javascript
// zero_chat_simple.html

let wakeWordRecognition = null;

function startWakeWordDetection() {
    if ('webkitSpeechRecognition' in window) {
        wakeWordRecognition = new webkitSpeechRecognition();
        wakeWordRecognition.continuous = true;
        wakeWordRecognition.interimResults = false;
        wakeWordRecognition.lang = 'he-IL';
        
        wakeWordRecognition.onresult = (event) => {
            const transcript = event.results[event.results.length - 1][0].transcript;
            console.log("שמעתי:", transcript);
            
            if (transcript.includes('זירו') || transcript.includes('zero')) {
                console.log("🔔 מילת השכמה זוהתה!");
                playBeep(); // צליל אישור
                startListeningForCommand();
            }
        };
        
        wakeWordRecognition.start();
        console.log("👂 מקשיב למילת השכמה 'זירו'...");
    }
}

function playBeep() {
    // צליל קצר שמאשר שזירו מקשיב
    const audioContext = new AudioContext();
    const oscillator = audioContext.createOscillator();
    oscillator.frequency.value = 800;
    oscillator.connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.1);
}

function startListeningForCommand() {
    // התחל הקלטה רגילה
    console.log("🎤 מקשיב לפקודה...");
    // הפעל את מערכת ההקלטה הרגילה
}

// הפעל בטעינת העמוד:
window.addEventListener('load', () => {
    startWakeWordDetection();
});
```

**תוצאה:**
- ✅ אמור "זירו" ודבר
- ✅ ידיים חופשיות - אין צורך ללחוץ
- ✅ חוויה כמו Siri/Alexa!

---

## 📊 **תוצאות צפויות - Phase 2:**

| תכונה | לפני | אחרי Phase 2 |
|-------|------|-------------|
| **הפעלה** | לחיצה על כפתור | "זירו" קולי ✅ |
| **הקלטה** | ידני (התחל/עצור) | אוטומטי ✅ |
| **הפרעות** | ממשיך לדבר | עוצר מיד ✅ |
| **הקשר** | שוכח | זוכר ✅ |
| **תחושה** | רובוטי | טבעי! 🗣️ |

---

## ⏱️ **זמן ביצוע משוער:**

1. **VAD** - 30 דקות
2. **Interrupt Handling** - 20 דקות
3. **Context-Aware** - 30 דקות
4. **Wake Word** - 20 דקות

**סה"כ:** ~1.5-2 שעות

---

## 💡 **המלצה:**

### **התחל עם:**
1. ✅ **VAD** - השיפור הכי מורגש!
2. ✅ **Context-Aware** - שיחה חכמה יותר
3. ⏸️ **Interrupt** - נחמד לאחר VAD
4. ⏸️ **Wake Word** - אופציונלי, אבל מגניב!

---

**מוכן להתחיל עם Phase 1 ואז Phase 2?** 🚀



