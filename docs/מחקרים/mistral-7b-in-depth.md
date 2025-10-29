# מדריך מעמיק ליישום הפקת תשובות עם Mistral 7B

---

## מבוא
Mistral 7B הוא מודל שפה מתקדם האופטימלי להפקת תשובות, ביצוע משימות NLU ויצירת תוכן. המדריך הבא יהפוך אותך ליעיל בתפעול, הטמעה ואופטימיזציה של תשובות המודל – בשרת/מחשב שלך או בענן.

---

## שלב 1: התקנה וטעינת המודל

### התקנת הספריות הדרושות:
```bash
pip install transformers accelerate sentencepiece bitsandbytes
```
במקרה של סביבת GPU בינונית/ביתית, כדאי להשתמש ב־4bit quantization להוריד עומס זיכרון.

### טעינה בסיסית ב־Python:
```python
from transformers import pipeline
pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2", device_map="auto")
result = pipe("הסבר על חשיבות מערכת החיסון", max_new_tokens=128)
print(result[0]['generated_text'])
```
להפעלה מהירה: ניתן להשתמש בממשק Ollama להרצה מקומית ([ollama.com](https://ollama.com/library/mistral))

---

## שלב 2: פרמטרים קריטיים וגישות להשפעה על איכות התשובה

| פרמטר        | משמעות | מתי להעלות/להוריד |
|--------------|--------|--------------------|
| temperature  | דרגת רנדומאליות (0.1-1.5) | נמוך – תשובה מדויקת
גבוה – תשובה יצירתית |
| top_p        | אחוז פיזור, nucleus sampling | גבוה – פלורליזם, יצירתיות. נמוך – דטרמיניסטי |
| top_k        | כמה אפשרויות נשקלות | בהגדרות גבוהות, תשובה פחות צפויה |
| max_new_tokens | כמות טוקנים בפלט  | שליטה על אורך התשובה (128–1024+) |
| presence/frequency penalty | עונש על חזרתיות (0-2) | למניעת לולאות/חזרות |

הערה: בדרך כלל ממליצים לשנות **או** temperature **או** top_p – לא שניהם יחד.[32][web:34]

---

## שלב 3: פורמט הודעות, prompting ודוגמאות

מודלי Mistral 7B עובד בצורה מיטבית עם פורמט מבוסס תגים ובניית prompt בשפת משתמש/assistant, לדוגמה:
```python
messages = [
    {"role": "user", "content": "[INST] תאר את מבנה התא [/INST]"},
]
inputs = tokenizer.apply_chat_template(messages, return_tensors='pt')
outputs = model.generate(**inputs, max_new_tokens=80)
reply = tokenizer.decode(outputs[0])
```
פירוט נוסף על עבודה עם chat template ניתן למצוא ב-Transformers doc וב-HuggingFace.[59][56]

דוגמה להתאמת prompt:
[s-1][INST] כתוב פסקה על בינה מלאכותית [/INST]

---

## שלב 4: Best practices ל־prompt engineering

- השתמש ב־system prompt עבור קביעת סגנון, טון/פורמט:
  - דוגמה: 'ענ/י בכבוד ובקצרה ולא בשפה גבוהה'
- הגדר פורמט פלט רצוי (רשימה, טבלה, JSON, קוד)
- תן דוגמה לפורמט התשובה המבוקש בתוך הפרומפט
- הגבל טוקנים במידת הצורך – כך תשלוט באורך הפלט
- עקוב אחרי חוזק (presence penalty) כדי למנוע חזרות[web:32][web:34]

---

## שלב 5: יישום מתקדם – עבודה עם API והרצה מקומית (Ollama)

### התקנה בסיסית ב־Ollama (ללא קוד):
1. מתקינים את ollama לפי מערכת ההפעלה
2. מריצים `ollama run mistral`
3. הפעלת בקשות למודל באמצעות REST API:
```python
import requests
prompt = "דוגמת פרומפט"
response = requests.post(
    "http://localhost:11434/api/generate",
    json={"model": "mistral", "prompt": prompt})
print(response.json()['response'])
```
[42][39]

---

## שלב 6: אופטימיזציה וביצועים

- הגדל batch size להרצת מקבילית במידת האפשר.
- עבור רצפים ארוכים (1024+): השתמש בקצבי prompt קצרים.
- הפחת context window במידת הצורך כדי לשפר latency.
- הרץ quantized model ב־4bit או 8bit להקטנת זיכרון ע"ח מהירות אם יש צורך.[39][web:43]

---

## שלב 7: טיפים ודגשים ל־prompt מורכב
- משלבים system + user + דוגמת פלט בתוך prompt.
- ממליצים על few-shot prompting (כלומר דוגמה עם פלט רצוי + השאלה שתרצה לפתור).
- שמור על מבנה עקבי – דיאלוג בסגנון:
  `<s>[INST] שאלה [/INST] תשובה שנבנתה </s><s>[INST] שאלה נוספת [/INST]`
- רוצה לחבר prompt ממספר הודעות? השתמש ב־apply_chat_template עם כמה שלבים.

---

## מקורות והעמקה
- [Mistral Docs - Sampling](https://docs.mistral.ai/capabilities/completion/sampling)
- [HuggingFace Transformers - Chat Templating](https://huggingface.co/docs/transformers/main/en/chat_templating)
- [Ollama Mistral Page](https://ollama.com/library/mistral)


---

### לדוגמות שיחה, fine-tuning מתקדם וטיפים נוספים – נספחים בקישורים לעיל.


