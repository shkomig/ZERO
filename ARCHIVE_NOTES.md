# UI Archive Notes

- הפנינו את `/` אל `/simple` כברירת מחדל.
- הנתיב `/advanced` הוגדר כמיושן ומפנה ל-`/simple`.
- קבצי UI ישנים מומלצים לארכוב: `zero_web_interface.html`, `zero_chat_advanced.html`, `zero_ui.html`.
- ניתן להעבירם לתיקיית `archive/ui/` לשמירה היסטורית; ההפניות אינן מסתמכות עליהם יותר.

דוגמה (Windows PowerShell):

```powershell
New-Item -ItemType Directory -Force -Path archive\ui
Move-Item zero_web_interface.html archive\ui\
Move-Item zero_chat_advanced.html archive\ui\
Move-Item zero_ui.html archive\ui\
```
