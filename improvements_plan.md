# 🔧 תוכנית שיפורים ל-Zero Agent

## 📊 בעיות מזוהות:

### 1. 🌐 חיפוש באינטרנט לא מביא מידע עדכני
**בעיה:** DuckDuckGo API מוגבל ולא תמיד מחזיר תוצאות טובות
**פתרון:** שילוב מספר מקורות חיפוש + scraping אמיתי

### 2. 📝 תשובות קצרות מדי
**בעיה:** ה-LLM מחזיר תשובות קצרות ולא מפורטות
**פתרון:** System prompt משופר + הנחיות ברורות

### 3. 💭 חוסר הקשר בין שיחות
**בעיה:** Zero לא זוכר שיחות קודמות
**פתרון:** שיפור Memory Management + Context Window

---

## 🚀 יישום השיפורים:

### שיפור 1: WebSearch משופר
- [ ] הוספת Google Finance API למניות
- [ ] הוספת Yahoo Finance כ-fallback
- [ ] scraping ישיר מדפי תוצאות
- [ ] cache לתוצאות חיפוש

### שיפור 2: תשובות מפורטות יותר
- [ ] System prompt חדש עם הנחיות ברורות
- [ ] הגדרת min_length לתשובות
- [ ] הוספת "context expansion" - Zero ישאל שאלות הבהרה

### שיפור 3: Memory משופר
- [ ] שמירת 10 השיחות האחרונות בזיכרון
- [ ] סיכום אוטומטי של שיחות ארוכות
- [ ] זיהוי נושאים חוזרים
- [ ] "conversation threads" - עקיבה אחר נושא לאורך זמן

---

## 📅 סדר ביצוע:
1. WebSearch - חיוני ביותר
2. System Prompt - קל ליישום
3. Memory - דורש זמן

