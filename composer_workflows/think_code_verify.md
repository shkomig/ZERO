## Cursor 2.0 Composer Workflow: Think → Code → Verify (Zero)

מטרה: להריץ תהליך תלת־שלבי דרך Composer שמדבר עם ה־API המקומי (`/api/chat`).

שלבים מוצעים:
1) Think (smart): ניתוח ותכנון בעברית.
2) Code (coder): מימוש קוד נקי ומתועד לפי התוכנית.
3) Verify (smart): בדיקת נכונות, ביצועים,边, תיקונים.

Endpoint: `POST http://localhost:8080/api/chat`

Payload בסיסי:
```json
{
  "message": "...",
  "model": "smart|coder|expert|fast",
  "use_memory": true,
  "conversation_history": []
}
```

דוגמאות טריגר ל-Composer:
- On Save (קבצים מסוימים): מריץ שלב Verify בלבד עם תמצות diff.
- On PR Open: מריץ שלושת השלבים ומצרף תוצאות כתגובה ל-PR.

הרצה מקומית מקבילה:
```bash
python workflows/think_code_verify.py "בנה מודול שמחשב מדד X ומחזיר גרף"
```

הערות:
- ניתן להחליף `smart` ב-`expert` למשימות עמוקות, ולשנות פרומפטים בהתאם.
- מומלץ להעביר היסטוריה מצטברת בין השלבים לדיוק גבוה יותר.


