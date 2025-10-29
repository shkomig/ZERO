# תוכנית מעבר ל-DictaLM 2.0 - תיעוד מקיף

**תאריך:** 29 אוקטובר 2025  
**גרסה:** 1.1  
**מטרה:** מעבר מ-Mixtral 8x7B בסיסי ל-DictaLM 2.0 לשיפור איכות העברית

---

## 📋 תוכן עניינים
1. [רקע ומוטיבציה](#רקע-ומוטיבציה)
2. [ניתוח מצב נוכחי](#ניתוח-מצב-נוכחי)
3. [מה זה DictaLM 2.0](#מה-זה-dictalm-20)
4. [הוראות התקנה מפורטות](#הוראות-התקנה-מפורטות)
5. [שינויים נדרשים בקוד](#שינויים-נדרשים-בקוד)
6. [תוכנית גיבוי ושחזור](#תוכנית-גיבוי-ושחזור)
7. [בדיקות איכות](#בדיקות-איכות)
8. [סיכונים והתמודדות](#סיכונים-והתמודדות)

---

## 🎯 רקע ומוטיבציה

### בעיות מזוהות במערכת הנוכחית

#### 1. בעיות דקדוק עברי חמורות
**דוגמה מתועדת:**
```
❌ לפני: "ברוכים חברים, אציג שני הפסדים המרכזיים..."
✓ אחרי (צפוי): "טיעונים בעד:\n1. שמירה על פרטיות..."
```

**בעיות ספציפיות:**
- המצאת מילים לא תקניות ("הפסדים" במקום "טיעונים")
- שימוש בצירופים שגויים ("רגולציה ממשלתית מסוג מגברת")
- פתיחות מיותרות ("ברוכים חברים")
- מבנה לא ברור

#### 2. פער בפרמטרים
**ממצא קריטי מהמחקר:**
- טמפרטורה נוכחית: **0.5** (גבוהה מדי!)
- טמפרטורה מומלצת: **0.1-0.2** (להפחתת הזיות)
- **זה מסביר את רוב הבעיות!**

#### 3. חוסר התאמה לעברית במודל הבסיסי
**ממצאים מהמחקר (`mixtral-8x7b-research.md`):**
- Mixtral 8x7B בסיסי **לא מותאם לעברית**
- יחס טוקניזציה: **5.81 טוקנים למילה** (גבוה מאוד!)
- המלצה מפורשת: "**עבור משתמשים דוברי עברית, מומלץ לשקול שימוש במודלים המותאמים במיוחד לשפה**"

### למה DictaLM 2.0?

**מהמחקר:**
> "DictaLM 2.0: מודל מתקדם המבוסס על מיסטרל עם אימון דו-לשוני"

**יתרונות צפויים:**
1. ✅ **אימון ייעודי על עברית** - דקדוק מושלם
2. ✅ **טוקניזר מותאם** - יחס טוקנים נמוך יותר
3. ✅ **הבנה טובה יותר של הקשר עברי** - תרבות וניואנסים
4. ✅ **תמיכה דו-לשונית** - אנגלית + עברית ברמה גבוהה
5. ✅ **גרסת GGUF מוכנה** - קוונטיזציה Q4_K_M (מאוזנת)

---

## 🔍 ניתוח מצב נוכחי

### קבצים מעורבים במערכת LLM

#### 1. `streaming_llm.py` - המנוע הראשי
```python
# שורות 21-58: הגדרת מודלים
MODELS = {
    "expert": {"name": "mixtral:8x7b", ...},  # ← המודל הנוכחי
    ...
}

# שורה 61: מודל ברירת מחדל
default_model: str = "expert"  # ← מצביע על mixtral:8x7b

# שורות 95-109: פרמטרים
"temperature": 0.5,         # ← צריך 0.15!
"top_p": 0.9,
"top_k": 40,
```

#### 2. `enhanced_system_prompt.py` - הנחיות המערכת
- 337 שורות של הנחיות מפורטות
- **בעיה:** לא משתמש בתבנית `[INST]...[/INST]`

#### 3. `api_server.py` - שרת ה-API
- שורות 1133-1167: בניית הפרומפט
- שורות 1183-1213: טיפול ב-Chain-of-Thought

### תלויות ואינטגרציות
```
streaming_llm.py
    ↓ משמש ב-
api_server.py (שורה 45)
    ↓ משתמש ב-
enhanced_system_prompt.py
    ↓ נשלח אל
Ollama Server (localhost:11434)
    ↓ מפעיל את
mixtral:8x7b (מודל נוכחי)
```

---

## 📚 מה זה DictaLM 2.0

### פרטי טכניים

**מקור:**
- **פיתוח:** Dicta (ארגון ישראלי לעיבוד שפה עברית)
- **מחקר:** https://arxiv.org/abs/2407.07080
- **Hugging Face:** https://huggingface.co/dicta-il/dictalm2.0-GGUF

**גרסה זמינה:**
- **שם קובץ:** `dictalm2.0.Q4_K_M.gguf`
- **גודל:** ~4-5GB (קוונטיזציה Q4)
- **איכות:** Q4_K_M = איזון מצוין בין איכות לביצועים
- **בסיס:** Mistral architecture עם אימון דו-לשוני

**מאפיינים:**
- אימון על טקסטים עבריים מגוונים
- טוקניזר מותאם לעברית (יחס טוקנים נמוך יותר)
- תמיכה מלאה באנגלית
- אופטימיזציה למשימות הוראה (Instruct)

---

## 🔧 הוראות התקנה מפורטות

### שלב 1: הורדת המודל מ-HuggingFace

#### Windows (PowerShell):
```powershell
# צור תיקיית הורדות
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Downloads\DictaLM"
cd "$env:USERPROFILE\Downloads\DictaLM"

# הורד את המודל (הקובץ גדול - ייקח כמה דקות)
# אופציה 1: דרך דפדפן
Start-Process "https://huggingface.co/dicta-il/dictalm2.0-GGUF/blob/main/dictalm2.0.Q4_K_M.gguf"
# לחץ על כפתור "Download"

# אופציה 2: דרך Hugging Face CLI (אם מותקן)
huggingface-cli download dicta-il/dictalm2.0-GGUF dictalm2.0.Q4_K_M.gguf --local-dir .
```

### שלב 2: יצירת Modelfile

צור קובץ בשם `Modelfile` (ללא סיומת) באותה תיקייה:

```bash
# Modelfile תוכן:
FROM "dictalm2.0.Q4_K_M.gguf"

# System message for Hebrew optimization
SYSTEM """אתה DictaLM 2.0 - מודל שפה מתקדם המותאם במיוחד לעברית."""

# Parameters optimized for Hebrew
PARAMETER temperature 0.15
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 16384

# Stop tokens
PARAMETER stop "[INST]"
PARAMETER stop "[/INST]"
PARAMETER stop "<|im_end|>"
```

**ליצירה ב-PowerShell:**
```powershell
cd "$env:USERPROFILE\Downloads\DictaLM"

@"
FROM "dictalm2.0.Q4_K_M.gguf"
SYSTEM ""אתה DictaLM 2.0 - מודל שפה מתקדם המותאם במיוחד לעברית.""
PARAMETER temperature 0.15
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_ctx 16384
"@ | Out-File -FilePath "Modelfile" -Encoding utf8 -NoNewline
```

### שלב 3: יצירת המודל ב-Ollama

```powershell
# ודא ש-Ollama רץ
Get-Process ollama -ErrorAction SilentlyContinue

# אם לא רץ, הפעל:
# Start-Process "C:\Users\<YourUsername>\AppData\Local\Programs\Ollama\ollama.exe"

# צור את המודל (זה לוקח 2-3 דקות)
cd "$env:USERPROFILE\Downloads\DictaLM"
ollama create dictalm -f Modelfile

# בדוק שהמודל נוצר
ollama list | Select-String "dictalm"
```

**פלט צפוי:**
```
transferring model data
using existing layer sha256:...
creating new layer sha256:...
writing manifest
success
```

### שלב 4: בדיקה בסיסית

```powershell
# בדיקה 1: שאלה פשוטה
ollama run dictalm "שלום, מה שלומך?"

# בדיקה 2: השאלה הבעייתית המקורית
ollama run dictalm "הצג את שני הטיעונים המרכזיים בעד ונגד רגולציה ממשלתית הדוקה של רשתות חברתיות גדולות"

# בדיקה 3: דקדוק
ollama run dictalm "הסבר מהו Machine Learning בעברית"
```

**קריטריוני הצלחה:**
- ✅ תגובה בעברית תקנית (ללא "ברוכים חברים")
- ✅ מבנה ברור (טיעונים בעד / נגד)
- ✅ ללא מילים מומצאות
- ✅ זמן תגובה סביר (< 15 שניות)

---

## 💻 שינויים נדרשים בקוד

### 1. עדכון `streaming_llm.py`

#### שינוי A: הוספת המודל החדש (שורות 30-36)
```python
"expert": {
    "name": "dictalm",  # ← שם המודל החדש ב-Ollama
    "description": "DictaLM 2.0 - Optimized for Hebrew with perfect grammar",
    "size": "4.5GB (Q4_K_M)",
    "speed": "⚡⚡⚡⚡",
    "quality": "⭐⭐⭐⭐⭐⭐ (עברית מושלמת)"
},
```

#### שינוי B: גיבוי המודל הישן (הוספה אחרי "expert")
```python
"expert-old": {
    "name": "mixtral:8x7b",
    "description": "Original Mixtral (backup)",
    "size": "26GB",
    "speed": "⚡⚡⚡",
    "quality": "⭐⭐⭐⭐⭐"
},
```

#### שינוי C: תיקון הטמפרטורה (שורות 103, 221)
```python
# שורה 103 (Streaming)
"temperature": 0.15,  # ← שינוי מ-0.5 ל-0.15!

# שורה 221 (Non-Streaming)
"temperature": 0.15,  # ← שינוי מ-0.5 ל-0.15!
```

#### שינוי D: הערות תיעוד
```python
# שורה 95 (לפני הפרמטרים)
# OPTIMIZED SETTINGS for DictaLM 2.0 - MAXIMUM HEBREW QUALITY
# Based on research: temperature 0.15 reduces hallucinations drastically
payload = {
    ...
```

### 2. עדכון `enhanced_system_prompt.py`

#### שינוי בשורה 8 (זהות המודל)
```python
DETAILED_SYSTEM_PROMPT = """אתה **DictaLM 2.0** – מודל שפה מתקדם המותאם במיוחד לעברית.
אימנת על קורפוס עברי ענק ויש לך הבנה עמוקה של דקדוק עברי, תחביר ותרבות ישראלית.
תפקידך: עוזר חכם, מדויק, מהיר ואמין – ידע נרחב במדעים, טכנולוגיה והיסטוריה.
```

### 3. אופציונלי: עדכון `api_server.py`

**אם DictaLM דורש תבנית ספציפית**, נוסיף (אחרי בדיקה):

```python
# שורות 1133-1167 (בניית הפרומפט)
# רק אם נדרש:
if model_name == "dictalm":
    prompt = f"<s>[INST] {system_prompt}\n\n{user_message} [/INST]"
else:
    prompt = f"{system_prompt}\n\n{user_message}"
```

---

## 💾 תוכנית גיבוי ושחזור

### לפני כל שינוי - צור גיבוי!

```powershell
# 1. צור תיקיית גיבוי
New-Item -ItemType Directory -Force -Path "backups\dictalm-migration-2025-10-29"

# 2. גבה קבצים קריטיים
Copy-Item "streaming_llm.py" "backups\dictalm-migration-2025-10-29\"
Copy-Item "enhanced_system_prompt.py" "backups\dictalm-migration-2025-10-29\"
Copy-Item "api_server.py" "backups\dictalm-migration-2025-10-29\"

# 3. צור Git branch
git checkout -b dictalm-migration
git add -A
git commit -m "backup: Pre-DictaLM migration state"

# 4. רשום את מצב Ollama הנוכחי
ollama list > "backups\dictalm-migration-2025-10-29\ollama-models-before.txt"
```

### תוכנית Rollback

**אם משהו לא עובד:**

#### שלב 1: עצור את השרת
```powershell
Get-Process python | Where-Object {$_.CommandLine -like '*api_server*'} | Stop-Process -Force
```

#### שלב 2: שחזר קבצים
```powershell
Copy-Item "backups\dictalm-migration-2025-10-29\streaming_llm.py" "." -Force
Copy-Item "backups\dictalm-migration-2025-10-29\enhanced_system_prompt.py" "." -Force
Copy-Item "backups\dictalm-migration-2025-10-29\api_server.py" "." -Force
```

#### שלב 3: אתחל מחדש
```powershell
python api_server.py
```

#### אופציה מהירה: שינוי זמני במודל בלי rollback
```python
# streaming_llm.py, שורה 31 - פשוט שנה בחזרה:
"expert": {"name": "mixtral:8x7b", ...}
```

---

## 🧪 בדיקות איכות

### סוויטת בדיקות מקיפה

צור קובץ `test_dictalm_quality.py`:

```python
"""
Test suite for DictaLM 2.0 quality validation
Tests the 5 critical scenarios
"""

import requests
import json
import time

BASE_URL = "http://localhost:8080/api/chat"

def send_query(message):
    """Send query to Zero Agent API"""
    try:
        response = requests.post(BASE_URL, json={"message": message}, timeout=60)
        return response.json()['response']
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_analytical_question():
    """Test 1: The problematic analytical question"""
    print("\n" + "="*70)
    print("TEST 1: Analytical Question (טיעונים בעד/נגד)")
    print("="*70)
    
    query = """הצג את שני הטיעונים המרכזיים בעד ונגד רגולציה ממשלתית 
הדוקה של רשתות חברתיות גדולות. השתמש בשפה עברית רשמית וניטרלית, 
תוך הקפדה על הפרדה ברורה בין הטיעונים."""
    
    response = send_query(query)
    print(f"\n📝 Response:\n{response}\n")
    
    # Checks
    checks = {
        "✅ יש 'טיעונים בעד'": "טיעונים בעד" in response or "בעד:" in response,
        "✅ יש 'טיעונים נגד'": "טיעונים נגד" in response or "נגד:" in response,
        "✅ אין 'ברוכים'": "ברוכים" not in response.lower(),
        "✅ אין 'אציג'": "אציג" not in response,
        "✅ אין מילים מומצאות": all(word not in response for word in ["הפסדים", "מגברת", "טפשית"]),
    }
    
    print("\n🔍 Validation:")
    for check, passed in checks.items():
        print(f"  {check if passed else check.replace('✅', '❌')}")
    
    return all(checks.values())

def test_cot_logic():
    """Test 2: Chain-of-Thought logic"""
    print("\n" + "="*70)
    print("TEST 2: Chain-of-Thought Logic")
    print("="*70)
    
    query = """בחדר יש 5 חתולים. לכל חתול יש 4 רגליים. 
כמה רגליים של בני אדם נמצאות בחדר, בהנחה שיש בחדר רק את מי שצריך 
כדי לספור את החתולים?"""
    
    response = send_query(query)
    print(f"\n📝 Response:\n{response}\n")
    
    # Expected: 2 רגליים
    checks = {
        "✅ מכיל '2'": "2" in response or "שתיים" in response or "שתי" in response,
        "✅ מכיל 'רגליים'": "רגליים" in response,
        "✅ ללא ערבוב עם חתולים": "20" not in response,
    }
    
    print("\n🔍 Validation:")
    for check, passed in checks.items():
        print(f"  {check if passed else check.replace('✅', '❌')}")
    
    return all(checks.values())

def test_grammar():
    """Test 3: Hebrew grammar quality"""
    print("\n" + "="*70)
    print("TEST 3: Hebrew Grammar")
    print("="*70)
    
    query = "תאר לי את ההבדלים בין בינה מלאכותית ללמידה עמוקה"
    
    response = send_query(query)
    print(f"\n📝 Response:\n{response}\n")
    
    forbidden = ["הפסדים", "מגברת", "טפשית בניסי", "עלול להעריך"]
    checks = {
        f"✅ אין '{word}'": word not in response
        for word in forbidden
    }
    checks["✅ יש תוכן מהותי"] = len(response) > 50
    
    print("\n🔍 Validation:")
    for check, passed in checks.items():
        print(f"  {check if passed else check.replace('✅', '❌')}")
    
    return all(checks.values())

def test_conciseness():
    """Test 4: Short and concise answers"""
    print("\n" + "="*70)
    print("TEST 4: Conciseness")
    print("="*70)
    
    query = "מהי עיר הבירה של ישראל?"
    
    response = send_query(query)
    print(f"\n📝 Response:\n{response}\n")
    
    word_count = len(response.split())
    checks = {
        "✅ תשובה קצרה (< 20 מילים)": word_count < 20,
        "✅ מכיל 'ירושלים'": "ירושלים" in response,
        "✅ ללא פתיחות מיותרות": not any(word in response for word in ["ברוכים", "אציג", "אסביר"]),
    }
    
    print(f"\n🔍 Validation (מספר מילים: {word_count}):")
    for check, passed in checks.items():
        print(f"  {check if passed else check.replace('✅', '❌')}")
    
    return all(checks.values())

def test_technical_terms():
    """Test 5: Technical terminology in Hebrew"""
    print("\n" + "="*70)
    print("TEST 5: Technical Terms")
    print("="*70)
    
    query = "הסבר מהו Latency במערכות מחשב"
    
    response = send_query(query)
    print(f"\n📝 Response:\n{response}\n")
    
    checks = {
        "✅ יש מונח עברי": any(term in response for term in ["זמן אחזור", "חהיון", "השהיה"]),
        "✅ הסבר ברור": len(response) > 30,
    }
    
    print("\n🔍 Validation:")
    for check, passed in checks.items():
        print(f"  {check if passed else check.replace('✅', '❌')}")
    
    return all(checks.values())

def run_all_tests():
    """Run all quality tests"""
    print("\n" + "="*70)
    print("🧪 DictaLM 2.0 Quality Test Suite")
    print("="*70)
    print(f"Server: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Analytical Question", test_analytical_question),
        ("Chain-of-Thought", test_cot_logic),
        ("Grammar Quality", test_grammar),
        ("Conciseness", test_conciseness),
        ("Technical Terms", test_technical_terms),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n🎯 Score: {passed_count}/{total_count} ({100*passed_count//total_count}%)")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! DictaLM 2.0 is ready for production!")
    elif passed_count >= total_count * 0.8:
        print("\n⚠️  Most tests passed, minor adjustments may be needed")
    else:
        print("\n❌ Several tests failed. Review needed before production")
    
    return passed_count == total_count

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
```

### הרצת הבדיקות

```powershell
# ודא שהשרת רץ
# אז הרץ:
python test_dictalm_quality.py
```

---

## ⚠️ סיכונים והתמודדות

### סיכון 1: ביצועים איטיים
**סבירות:** נמוכה (Q4 יעיל)  
**פתרון:**
- בדוק שימוש GPU: Task Manager → Performance
- אם CPU-only, שקול Q3 או Q2

### סיכון 2: תאימות תבנית הנחיות
**סבירות:** בינונית  
**פתרון:**
- בדוק עם Ollama ישירות קודם
- התאם את `api_server.py` לפי הצורך

### סיכון 3: עדיין בעיות דקדוק
**סבירות:** נמוכה (DictaLM אימן על עברית)  
**פתרון:**
- התאם את System Prompt
- הפחת טמפרטורה עוד יותר (0.1)

---

## ✅ Checklist סופי

### לפני התחלה
- [ ] קראתי את כל המסמך
- [ ] יש לי גיבוי מלא
- [ ] יצרתי Git branch
- [ ] יש לי 3 שעות פנויות
- [ ] השרת הנוכחי עובד

### התקנה
- [ ] הורדתי `dictalm2.0.Q4_K_M.gguf`
- [ ] יצרתי `Modelfile`
- [ ] הרצתי `ollama create dictalm`
- [ ] בדקתי עם `ollama list`
- [ ] בדקתי תשובה בסיסית

### שינויי קוד
- [ ] עדכנתי `streaming_llm.py` (שם מודל)
- [ ] תיקנתי טמפרטורה (0.5 → 0.15)
- [ ] עדכנתי `enhanced_system_prompt.py` (זהות)
- [ ] יצרתי `test_dictalm_quality.py`

### בדיקות
- [ ] עצרתי את השרת הישן
- [ ] הרצתי `python api_server.py`
- [ ] הרצתי `python test_dictalm_quality.py`
- [ ] כל הבדיקות עברו בהצלחה

### סיום
- [ ] תיעדתי תוצאות
- [ ] commit ל-Git
- [ ] merge ל-main
- [ ] עדכון CHANGELOG

---

## 📊 מדדי הצלחה

### קריטריונים לאישור Production

1. **דקדוק:** 0 שגיאות דקדוק בכל 5 הבדיקות
2. **מבנה:** 100% תאימות למבנה "טיעונים בעד/נגד"
3. **מהירות:** < 15 שניות לתשובה (Q4)
4. **ללא הזיות:** אין מילים מומצאות או פתיחות מיותרות
5. **סקור בדיקות:** 5/5 PASS

---

## 📞 נקודות עצירה והחלטה

עצור ושאל אם:
1. ההורדה נכשלת
2. `ollama create` מחזיר שגיאה
3. הבדיקה הבסיסית נכשלת
4. השרת לא עולה
5. יותר מבדיקה אחת נכשלת

---

**סטטוס:** ✅ מסמך מוכן - ממתין לאישור להתחלה!

**זמן משוער:** 2-3 שעות (כולל הורדה)

