ZERO - פיתוח שאילתות עם הקשר מסונכרן, Embeddings ואוטומציה חכמה
1. שאילתות עם הקשר מסונכרן (Synchronized Contextual Queries)
שלח שאילתות למודל AI שכוללות הקשר עשיר שנאסף ממסכי עבודה קודמים, טקסטים, ואירועים בודדים במערכת

כך המודל מבין טוב יותר את ההקשר ועונה בצורה מדויקת ומותאמת

בניית חלון הקשר מתאפשר על ידי ארגון מידע רלוונטי מראש (למשל 24 שעות אחרונות)

דוגמת קוד ליצירת פרומפט דינמי מחלון הקשר באסינכרון:

python
async def build_and_query(context_items: list[str], query: str, model_name: str):
    context_str = "\n\n".join(context_items)
    prompt = f\"\"\"Context:\n{context_str}\n\nQuery:\n{query}\"\"\"
    response = await model_manager.query_model(model_name, prompt, context_str)
    return response
2. שילוב Embeddings למנוע חיפוש סמנטי
יצירת וקטורי embedding מכל הטקסטים, סימונים ונתונים על המסך, כדי לאפשר חיפוש מבוסס משמעות וקרבה סמנטית

שימוש בכלי כמו ChromaDB, FAISS או Pinecone (במקרה זה מומלץ ChromaDB מקומית לפי ZERO)

אינטגרציה בין Embeddings לשאילתות ה-AI לקבלת תוצאות חכמות יותר

דוגמה ליצירת embedding ושאילתא:

python
def create_embedding(text: str) -> list[float]:
    # שימוש במודל AI ליצירת וקטור embedding
    return model_manager.get_embedding(text)

def semantic_search(query: str, vector_db, top_k=5):
    query_emb = create_embedding(query)
    results = vector_db.search(query_emb, k=top_k)
    return results
3. אוטומציה חכמה (Smart Automation)
שכבה שמגיבה לתשובות ה-AI ומפעילה פקודות אוטומטיות במחשב או ב-web

שילוב של PyAutoGUI לאוטומציות מקומיות ושל Playwright לאוטומציה מבוססת DOM לפרויקטים על דפדפן

יכולת לזהות מתי לבצע פעולה, לאזן בין אוטומציה לגורם אנושי, ולנהל שגיאות וחזרה על פעולות במידת הצורך

דוגמת קוד לפעולה אוטומטית:

python
import pyautogui

def automate_click(x: int, y: int):
    pyautogui.moveTo(x, y)
    pyautogui.click()

async def playwright_gmail_read(page):
    await page.goto('https://mail.google.com/mail/u/0/#inbox')
    emails = await page.query_selector_all('div.xT > div.y6 > span.bog')
    for email in emails:
        print(await email.inner_text())
טיפים לפיתוח עם Cursor
השתמש בפרומפטים מפורטים עם הפניה לקובץ זה ודוגמאות הקוד

התחל עם מימוש אסינכרוני ואמינות לטיפול בטעויות

תעדף שמירת פרטיות מלאה ונתונים בטוחים

עבד אינטראקטיבית: תעדכן את ההקשר באופן שוטף כדי לייעל תשובות AI

תשלב אפשרויות fallback חכמות (OCR במקרה של DOM לא נגיש)