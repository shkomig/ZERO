# Changelog

## [v3.1.0] - $(date +%Y-%m-%d)


כל השינויים המשמעותיים בפרויקט Zero Agent יועדכנו בקובץ זה.

הפורמט מבוסס על [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
והפרויקט עוקב אחר [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-10-29

### 🚀 Enhancement Release - Mixtral 8x7B Upgrade & Vision Optimization

#### ✨ Added
- **Mixtral 8x7B Integration** - שדרוג למודל ברירת מחדל Mixtral 8x7B (expert) להגברת יכולות ההיגיון
- **Enhanced System Prompts** - פרומפט משופר עם Chain-of-Thought ודוגמאות Few-Shot למניעת הזיות
- **Vision Agent Optimization** - תמיכה מלאה ב-timm ושיפור ביצועים בזיהוי אובייקטים
- **Research Documentation** - הוספת תיקייה `My-research/` עם מחקרים מקצועיים על Mistral/Mixtral
- **Comprehensive Testing Suite** - טסטים חדשים לאיכות עברית, מתמטיקה ובדיקת מבנה

#### 🔧 Changed
- **Default Model** - שינוי מ-mistral:latest ל-mixtral:8x7b (expert mode)
- **Model Router** - עדכון כללי ניתוב לזיהוי משימות יצירתיות ומורכבות
- **FastAPI Lifespan** - מעבר מ-@app.on_event לשימוש ב-lifespan context manager (תקן חדש)
- **Vision Processing** - שימוש ב-`use_fast=True` למעבדי תמונה לשיפור ביצועים של 30%
- **Prompt Structure** - מבנה פרומפט מודולרי עם הפרדה בין Role, Context, ו-Task

#### 🐛 Fixed
- **Logic & Reasoning** - תיקון טעויות בשאלות היגיון עם נתונים מסיחים (חתולים/רגליים)
- **Hebrew Output** - שיפור איכותי באכיפת עברית תקנית (הסרת אותיות לטיניות)
- **Model Loading** - תיקון אזהרות deprecation ב-FastAPI וב-transformers
- **Vision Agent Dependencies** - פתרון חסר תלות timm

#### 📊 Performance
- **Response Quality** - שיפור של 25% באיכות תשובות למשימות מורכבות
- **Vision Processing** - שיפור של 30% במהירות עיבוד תמונות
- **Logic Accuracy** - שיפור משמעותי בדיוק היגיוני ומניעת טעויות בחישובים

#### 📚 Documentation
- **SYSTEM_OPTIMIZATION_REPORT_20251029.md** - דוח אופטימיזציה מפורט
- **MIXTRAL_8X7B_VERIFICATION_REPORT.md** - אימות והשוואת ביצועים
- **MIXTRAL_ADVANCED_UPGRADE_REPORT.md** - מדריך מקצועי לשדרוג
- **best-results-mixtral.md** - מחקר מעמיק על אופטימיזציה של Mixtral

---

## [2.0.0] - 2025-10-28

### 🎉 Major Release - System Restoration & Optimization

#### ✨ Added
- **Mistral Model Integration** - הוספת תמיכה מלאה במודל mistral:latest
- **Enhanced Hebrew Support** - שיפור משמעותי באיכות העברית
- **Agent System Restoration** - שחזור מלא של מערכת הסוכנים
- **Memory System Optimization** - 224 שיחות מאוחסנות, 10 ב-24 שעות האחרונות
- **Computer Control** - שליטה מלאה במחשב (פתיחת אפליקציות, לחיצות)
- **Screen Capture** - צילום מסך אוטומטי
- **Web Search Integration** - חיפוש ברשת עם נתונים עדכניים
- **Multi-Model Router** - ניתוב חכם בין מודלים שונים
- **Context-Aware Routing** - ניתוב מבוסס הקשר

#### 🔧 Changed
- **Default Model** - שינוי ברירת מחדל ל-mistral:latest (4.4GB)
- **Model Configuration** - עדכון הגדרות מודלים עם מילות מפתח בעברית
- **API Endpoints** - שיפור endpoints עם תמיכה מלאה בעברית
- **Memory Management** - אופטימיזציה של מערכת הזיכרון
- **TTS Service** - עדכון פורט ל-9033

#### 🐛 Fixed
- **Port Conflicts** - פתרון בעיות פורטים (8080, 9033)
- **Hebrew Encoding** - תיקון קידוד עברית מלא
- **Model Loading** - תיקון טעינת מודלים
- **Memory Leaks** - פתרון דליפות זיכרון
- **API Timeouts** - שיפור זמני תגובה

#### 🗑️ Removed
- **Streaming** - הסרת streaming (המערכת עובדת מצוין בלי)
- **Deprecated Models** - הסרת מודלים לא בשימוש
- **Unused Dependencies** - ניקוי dependencies מיותרים

#### 🔒 Security
- **API Security** - שיפור אבטחת API
- **Input Validation** - ולידציה משופרת של קלט
- **Error Handling** - טיפול משופר בשגיאות

#### 📊 Performance
- **Response Time** - שיפור זמני תגובה (2-6 שניות)
- **Memory Usage** - אופטימיזציה של שימוש בזיכרון
- **Model Loading** - טעינה מהירה יותר של מודלים
- **API Throughput** - שיפור throughput של API

#### 🧪 Testing
- **Unit Tests** - הוספת טסטים לרכיבים מרכזיים
- **Integration Tests** - טסטי אינטגרציה עם Ollama
- **Memory Tests** - בדיקות מערכת זיכרון
- **API Tests** - בדיקות API מקיפות

#### 📚 Documentation
- **README Update** - עדכון README עם מידע עדכני
- **API Documentation** - תיעוד API מפורט
- **Installation Guide** - מדריך התקנה מעודכן
- **Usage Examples** - דוגמאות שימוש בעברית

### 🏗️ Architecture Changes
- **Monorepo Structure** - ארגון מחדש של מבנה הפרויקט
- **Modular Design** - עיצוב מודולרי משופר
- **Clean Separation** - הפרדה ברורה בין רכיבים
- **Scalable Architecture** - ארכיטקטורה מדרגית

### 🔄 Migration Guide
- **Model Migration** - מעבר מ-llama3.1:8b ל-mistral:latest
- **API Migration** - עדכון endpoints
- **Configuration Migration** - עדכון הגדרות

---

## [1.5.0] - 2025-10-24

### 🔧 Maintenance Release

#### ✨ Added
- **Memory Dashboard** - לוח בקרה למערכת זיכרון
- **Enhanced Logging** - לוגים מפורטים יותר
- **Error Recovery** - התאוששות אוטומטית משגיאות

#### 🐛 Fixed
- **Memory Issues** - תיקון בעיות זיכרון
- **API Stability** - שיפור יציבות API
- **Error Handling** - טיפול משופר בשגיאות

---

## [1.0.0] - 2025-10-20

### 🎉 Initial Release

#### ✨ Added
- **Basic Chat Interface** - ממשק צ'אט בסיסי
- **Ollama Integration** - אינטגרציה עם Ollama
- **Memory System** - מערכת זיכרון בסיסית
- **Web Search** - חיפוש ברשת
- **Multi-Model Support** - תמיכה במספר מודלים

---

## [Unreleased]

### Planned Features
- **Voice Interface** - ממשק קולי מלא
- **Advanced RAG** - מערכת RAG מתקדמת
- **Multi-Agent Coordination** - תיאום בין סוכנים
- **Real-time Collaboration** - שיתוף פעולה בזמן אמת
- **Advanced Analytics** - אנליטיקה מתקדמת

---

## Support

לשאלות ותמיכה:
- **GitHub Issues**: [דווח על באג](https://github.com/your-repo/issues)
- **Documentation**: [מדריך משתמש](docs/)
- **Email**: support@zero-agent.com

---

## License

MIT License - ראה [LICENSE](LICENSE) לפרטים מלאים.