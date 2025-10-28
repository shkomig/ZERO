# 📋 אסטרטגיית GitHub לפרויקט Zero Agent

## 🎯 מבוא - למה צריך את זה עכשיו?

הפרויקט שלך נמצא **בשלב קריטי**: יש לך כבר מערכת עובדת עם:
- Agent Orchestrator מתפקד ✅
- RAG + Memory system ✅  
- Multi-model support (Ollama, DeepSeek, Llama) ✅
- Web interface עם Claude UI ✅
- WebSearch + Stock prices ✅

**הבעיה:** הקוד לא מאורגן, אין branching strategy, commits לא מתועדים טוב.

**הפתרון:** יישום הפרקטיקות מהמסמך **בצורה הדרגתית** כדי לא להפריע לפיתוח.

---

## 📊 שלב 1: Branching Strategy (התחל מחר!)

### המלצה: **Simplified GitHub Flow**

למה דווקא זה?
- ✅ **פשוט** - לא צריך לזכור הרבה כללים
- ✅ **מהיר** - אתה עובד לבד, אין צוות גדול
- ✅ **גמיש** - אפשר לשנות במהירות

```
main (תמיד עובד, production-ready)
  ├── feature/enhanced-websearch    ← התכונה שהוספנו היום
  ├── feature/detailed-prompts      ← System prompts משופרים
  ├── feature/memory-improvement    ← הבא בתור
  ├── fix/unicode-encoding          ← תיקוני באגים
  └── hotfix/critical-server-crash  ← דחוף בלבד!
```

### כללי שמות Branches:

```bash
# תכונות חדשות
feature/artifact-panel
feature/stock-search
feature/claude-ui

# תיקוני באגים
fix/memory-leak
fix/websearch-timeout
fix/ui-mobile-responsive

# תיקונים דחופים (רק אם המערכת קרסה!)
hotfix/server-crash
hotfix/ollama-connection

# ניסויים (לא בטוח אם תמזג)
experiment/voice-interface
experiment/multi-language
```

### תהליך עבודה יומי:

```bash
# בוקר - מתחיל תכונה חדשה
git checkout main
git pull origin main
git checkout -b feature/memory-context-window

# עובד על התכונה...
# עורך קבצים, בודק...

# סיום יום - commit
git add .
git commit -m "feat(memory): add 10-conversation context window"
git push origin feature/memory-context-window

# מוכן למזג?
# פתח PR ב-GitHub
# אם הכל עובד - Merge!
git checkout main
git merge feature/memory-context-window
git push origin main
```

---

## 🏷️ שלב 2: Conventional Commits (התחל מהיום!)

### למה זה משנה?

1. **אוטומציה של גרסאות** - `feat` = v1.1.0, `fix` = v1.0.1
2. **Changelog אוטומטי** - כל השינויים בקובץ
3. **הבנה מהירה** - רואים מיד מה השתנה

### המבנה:

```
<type>(scope): <description>

[optional body]

[optional footer]
```

### Types שתשתמש בהם הכי הרבה:

```bash
# ✨ תכונה חדשה (→ מגדיל MINOR version: 1.2.0 → 1.3.0)
feat(websearch): add Yahoo Finance stock prices
feat(ui): implement Claude-style artifacts panel
feat(memory): add conversation threading

# 🐛 תיקון באג (→ מגדיל PATCH version: 1.2.0 → 1.2.1)
fix(rag): resolve ChromaDB timeout after 5 seconds
fix(ui): fix mobile responsive layout
fix(encoding): resolve unicode errors in terminal

# 📝 תיעוד (לא משפיע על version)
docs: add API usage examples
docs(readme): update installation guide

# 🎨 סגנון/פורמט (לא משפיע על version)
style: remove rocket emoji from logo
style(ui): update button colors to Claude palette

# ♻️ Refactoring (לא משפיע על version)
refactor(orchestrator): simplify task planning logic
refactor: extract system prompt to separate file

# ⚡ ביצועים (→ PATCH version)
perf(llm): reduce context window for faster responses
perf(cache): add 5-minute cache for web search

# 🧪 טסטים (לא משפיע על version)
test(agent): add tests for orchestrator execution
test: add unit tests for memory manager

# 🔧 תחזוקה (לא משפיע על version)
chore: update dependencies
chore(deps): bump ollama version to 0.5.0

# 💥 שינוי BREAKING (→ מגדיל MAJOR version: 1.2.0 → 2.0.0)
feat(api)!: change chat endpoint to require auth token

BREAKING CHANGE: /api/chat now requires Bearer token
```

### דוגמאות מהקוד שלך:

**מה שעשינו היום:**
```bash
git commit -m "feat(websearch): add enhanced search with stock market support

- Add Yahoo Finance API integration
- Smart detection of stock queries vs regular search
- 5-minute cache for search results
- Improved DuckDuckGo HTML parsing"

git commit -m "feat(prompts): implement detailed system prompts

- Add 150-300 word detailed mode
- Keep concise mode as option
- Include few-shot examples
- Structured response format with headers"

git commit -m "style(ui): update buttons to Claude-style design

- Replace filled buttons with bordered style
- Add btn-primary, btn-success, btn-warning variants
- Remove rocket emoji from logo"
```

---

## 📁 שלב 3: מבנה Repository (יישום הדרגתי)

### המצב הנוכחי שלך:

```
ZERO/
├── api_server.py
├── tool_websearch.py
├── tool_codeexecutor.py
├── memory/
├── zero_agent/
└── zero_web_interface.html
```

**בעיה:** הכל מעורבב, קשה למצוא דברים.

### המבנה המומלץ (מעבר הדרגתי!):

```
ZERO/
├── .github/                          # ← חדש! GitHub workflows
│   ├── workflows/
│   │   ├── ci.yml                    # בדיקות אוטומטיות
│   │   └── release.yml               # יצירת גרסאות
│   └── CODEOWNERS                    # מי אחראי על מה
│
├── src/                              # ← עבור בהדרגה
│   ├── core/                         # Core functionality
│   │   ├── api_server.py
│   │   ├── model_router.py
│   │   └── llm_interface.py
│   │
│   ├── agents/                       # Agent system
│   │   ├── orchestrator.py
│   │   ├── task_planner.py
│   │   └── safety_layer.py
│   │
│   ├── tools/                        # Tools
│   │   ├── websearch_improved.py
│   │   ├── code_executor.py
│   │   ├── gmail.py
│   │   └── calendar.py
│   │
│   ├── memory/                       # Memory system
│   │   ├── memory_manager.py
│   │   ├── rag_connector.py
│   │   └── short_term_memory.py
│   │
│   └── ui/                           # UI files
│       └── zero_web_interface.html
│
├── tests/                            # ← חדש! טסטים
│   ├── test_agent_system.py
│   ├── test_websearch.py
│   └── test_memory.py
│
├── docs/                             # ← חדש! תיעוד
│   ├── API_USAGE_GUIDE.md
│   ├── IMPROVEMENTS_SUMMARY.md
│   └── AGENT_SYSTEM_COMPLETE.md
│
├── scripts/                          # ← חדש! סקריפטים
│   ├── setup.sh
│   ├── backup.sh
│   └── deploy.sh
│
├── .gitignore                        # ← עדכן!
├── requirements.txt
├── README.md                         # ← עדכן עם מבנה חדש
└── CHANGELOG.md                      # ← חדש! אוטומטי
```

### תוכנית מעבר (3 שלבים):

#### שלב 1: הוסף תיקיות חדשות (השבוע)
```bash
mkdir -p .github/workflows
mkdir -p tests
mkdir -p docs
mkdir -p scripts

# העבר קבצי תיעוד
mv API_USAGE_GUIDE.md docs/
mv IMPROVEMENTS_SUMMARY.md docs/
mv AGENT_SYSTEM_COMPLETE.md docs/
```

#### שלב 2: העבר קבצים בהדרגה (שבוע הבא)
```bash
mkdir -p src/core src/agents src/tools src/memory src/ui

# העבר קבצים אחד אחד, בדוק שהכל עובד
git mv api_server.py src/core/
git commit -m "refactor: move api_server to src/core"

# המשך...
```

#### שלב 3: עדכן imports (שבועיים)
```python
# לפני:
from tool_websearch import WebSearchTool

# אחרי:
from src.tools.websearch_improved import EnhancedWebSearchTool
```

---

## 🔄 שלב 4: CI/CD Workflow (אוטומציה!)

### Workflow 1: בדיקות אוטומטיות על כל commit

צור: `.github/workflows/ci.yml`

```yaml
name: CI - Tests and Checks

on:
  push:
    branches: [ main, feature/* ]
  pull_request:
    branches: [ main ]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pylint pytest
      
      - name: Run linter
        run: |
          pylint src/ --disable=all --enable=E,F
      
      - name: Run tests
        run: |
          pytest tests/ -v
      
      - name: Check imports
        run: |
          python -c "import sys; sys.path.insert(0, '.'); from src.core.api_server import app; print('OK')"
```

### Workflow 2: יצירת גרסאות אוטומטית

צור: `.github/workflows/release.yml`

```yaml
name: Release - Semantic Versioning

on:
  push:
    branches: [ main ]

jobs:
  release:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Get version from commits
        id: version
        uses: paulhatch/semantic-version@v5.4.0
        with:
          tag_prefix: "v"
          major_pattern: "/(BREAKING CHANGE|!)/"
          minor_pattern: "/feat:/"
          patch_pattern: "/fix:/"
          version_format: "${major}.${minor}.${patch}"
      
      - name: Create Release
        if: steps.version.outputs.changed == 'true'
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          echo "📦 New version: ${{ steps.version.outputs.version }}"
          gh release create v${{ steps.version.outputs.version }} \
            --title "Release ${{ steps.version.outputs.version }}" \
            --generate-notes
      
      - name: Update CHANGELOG
        if: steps.version.outputs.changed == 'true'
        run: |
          echo "## v${{ steps.version.outputs.version }} - $(date +%Y-%m-%d)" >> CHANGELOG.md
          echo "" >> CHANGELOG.md
          gh pr list --state merged --limit 10 --json title,number \
            --jq '.[] | "- \(.title) (#\(.number))"' >> CHANGELOG.md
          git add CHANGELOG.md
          git commit -m "docs: update CHANGELOG for v${{ steps.version.outputs.version }}"
          git push
```

**תוצאה:**
- כל `feat:` → גרסה חדשה אוטומטית (v1.1.0 → v1.2.0)
- כל `fix:` → תיקון (v1.1.0 → v1.1.1)
- `CHANGELOG.md` מתעדכן אוטומטית!

---

## 🏷️ שלב 5: Labels ו-Issues

### הגדר Labels בGitHub:

```bash
# בעיות
🐛 bug - תקלה במערכת
🔥 critical - דורש תיקון מיידי!

# תכונות
✨ feature - תכונה חדשה
🎨 enhancement - שיפור קיים
💡 idea - רעיון לעתיד

# תחומים
🤖 area:agents - מערכת הסוכנים
🧠 area:memory - זיכרון וRAG
🔍 area:tools - כלים (websearch, etc)
🎨 area:ui - ממשק משתמש
📚 area:docs - תיעוד

# סטטוס
🔄 status:in-progress - בעבודה
👀 status:review - ממתין לreview
🚫 status:blocked - חסום
✅ status:done - הושלם

# עדיפות
🔴 priority:high - גבוהה
🟡 priority:medium - בינונית
🟢 priority:low - נמוכה
```

### תבנית Issue:

```markdown
## 📝 תיאור
[תאר את הבעיה או הבקשה]

## 🎯 מטרה
[מה אתה רוצה להשיג?]

## 📋 משימות
- [ ] משימה 1
- [ ] משימה 2
- [ ] משימה 3

## 🔗 קישורים
- Related to #123
- Depends on #124

## 💡 הערות נוספות
[מידע נוסף]
```

---

## 🚀 תוכנית יישום (4 שבועות)

### שבוע 1: יסודות ✅
- [x] התחל להשתמש ב-Conventional Commits
- [ ] צור branch לכל תכונה חדשה
- [ ] צור `.gitignore` מסודר
- [ ] הוסף `README.md` עדכני

### שבוע 2: מבנה 📁
- [ ] צור תיקיות `.github/`, `tests/`, `docs/`, `scripts/`
- [ ] העבר קבצי תיעוד ל-`docs/`
- [ ] כתוב Workflow ראשון (CI)
- [ ] הגדר Labels ב-GitHub

### שבוע 3: אוטומציה 🤖
- [ ] הפעל Semantic Versioning Workflow
- [ ] צור `CHANGELOG.md` ראשוני
- [ ] הוסף טסטים ראשונים ל-`tests/`
- [ ] הגדר Branch Protection Rules

### שבוע 4: שיפורים 🎨
- [ ] העבר קבצים ל-`src/` (בהדרגה!)
- [ ] עדכן imports
- [ ] צור `CODEOWNERS`
- [ ] תעד את התהליך

---

## 📊 דוגמאות מהחיים (מהקוד שלך!)

### דוגמה 1: איך היית עובד עם התכונה החדשה של WebSearch

```bash
# 1. צור branch
git checkout -b feature/enhanced-websearch

# 2. עבוד על הקוד
# יצרת tool_websearch_improved.py

# 3. Commit עם Conventional Commits
git add tool_websearch_improved.py
git commit -m "feat(websearch): add Yahoo Finance stock prices integration

- Real-time stock prices via Yahoo Finance API
- Smart query detection (stock vs regular search)
- 5-minute results caching
- Fallback to DuckDuckGo if Yahoo fails

Resolves #42"

# 4. Push
git push origin feature/enhanced-websearch

# 5. פתח PR ב-GitHub עם תיאור:
## תיאור
מוסיף תמיכה במחירי מניות בזמן אמת דרך Yahoo Finance

## שינויים
- ✨ EnhancedWebSearchTool class
- 📈 search_stock() method
- 💾 Cache results for 5 minutes
- 🔍 Smart detection of stock queries

## בדיקות
- [x] Tested with SPY, QQQ, AAPL
- [x] Fallback works when Yahoo unavailable
- [x] Cache expires after 5 minutes

## Screenshots
[תמונה של SPY price]

Closes #42

# 6. Merge!
git checkout main
git merge feature/enhanced-websearch
git push origin main

# 7. Workflow אוטומטי יוצר Release v1.3.0 🎉
```

### דוגמה 2: תיקון באג במערכת

```bash
# 1. מישהו מצא באג - פתח Issue
# Issue #55: Unicode encoding error in terminal

# 2. צור hotfix branch
git checkout -b fix/unicode-encoding

# 3. תקן את הבעיה
git add enhanced_system_prompt.py
git commit -m "fix(prompts): resolve unicode encoding in terminal output

Replace emoji characters with ASCII equivalents to prevent
UnicodeEncodeError on Windows terminals with cp1255 encoding.

Fixes #55"

# 4. Push + PR
git push origin fix/unicode-encoding

# 5. Merge
git checkout main
git merge fix/unicode-encoding

# 6. Workflow יוצר v1.2.1 (patch bump) 🎉
```

---

## 🎯 סיכום - מה תרוויח?

### תרוויח בטווח הקצר (שבוע):
✅ **ניקיון** - קוד מסודר, קל למצוא דברים  
✅ **היסטוריה** - תדע מה שינית וקנדי  
✅ **ביטחון** - אפשר לחזור אחורה בקלות

### תרוויח בטווח הבינוני (חודש):
✅ **אוטומציה** - גרסאות ובדיקות אוטומטיות  
✅ **תיעוד** - CHANGELOG מתעדכן לבד  
✅ **מקצועיות** - פרויקט נראה רציני

### תרוויח בטווח הארוך (שנה):
✅ **שיתוף** - אחרים יכולים לתרום  
✅ **תחזוקה** - קל לשמור ולשדרג  
✅ **Scale** - המערכת יכולה לגדול

---

## 🚦 התחל מחר!

### 3 דברים לעשות **עכשיו**:

1. **התקן GitHub CLI** (אם אין):
```bash
# Windows (Scoop)
scoop install gh

# או הורד מ:
# https://cli.github.com/
```

2. **צור `.gitignore` ראשון**:
```bash
# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/

# Environment
.env
venv/
env/

# IDE
.vscode/
.idea/

# Project specific
workspace/
logs/
*.log
data/vectors/

# OS
.DS_Store
Thumbs.db
```

3. **התחל עם Conventional Commits מהיום**:
```bash
# כל commit מעכשיו:
git commit -m "feat(scope): description"
git commit -m "fix(scope): description"
git commit -m "docs: description"
```

---

**זהו! עכשיו יש לך תוכנית ברורה ליישום 🎉**

**שאלות? בעיות? אני פה לעזור!** 🚀

