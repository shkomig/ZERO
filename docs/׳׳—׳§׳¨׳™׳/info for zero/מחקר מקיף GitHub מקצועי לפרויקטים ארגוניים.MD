עכשיו אצור מחקר מקיף על ניהול GitHub מקצועי לפרויקט בנייה של מערכת.

## מחקר מקיף: ניהול GitHub מקצועי לפרויקטים ארגוניים

### מבוא - חשיבות ניהול נכון

ניהול GitHub מקצועי הוא הבסיס לפיתוח תוכנה מאורגן, בטוח ומדרגי. עבור פרויקטים גדולים - במיוחד מערכות מורכבות כמו שלך - ניהול נכון של הקוד, הגרסאות, והתהליכים מבטיח **שמירה על איכות**, **מניעת באגים**, **אפשרות ל-rollback מהיר**, ו**שיתוף פעולה יעיל בין צוותים**.[1][2][3]

***

### חלק 1: אסטרטגיות Branching

#### 1.1 שלוש האסטרטגיות המרכזיות

**Trunk-Based Development (מומלץ לצוותים זריזים)**:[4][5][6][7]
- כל המפתחים עובדים על ענף אחד ראשי (`main`)
- branches קצרי-חיים (1-2 ימים מקסימום)
- אינטגרציה רציפה עם בדיקות אוטומטיות
- מתאים ל-CI/CD מהיר

**יתרונות**:[5][6]
- פחות סיבוכים במיזוג
- פידבק מהיר
- תמיד ב-production-ready state

**מתי להשתמש**:[7]
- צוותים קטנים-בינוניים (2-15 מפתחים)
- פריסה תכופה (יומית-שבועית)
- תרבות של automated testing חזקה

---

**GitHub Flow (פשוט ואפקטיבי)**:[4][7]
```
main (production-ready)
  ↓
feature/new-feature
  ↓
Pull Request → Review → Merge
```

**תהליך**:[4]
1. צור branch מ-`main`
2. פתח feature
3. פתח PR עם תיאור ברור
4. עבור code review
5. מזג ל-`main`
6. פרוס מיד

**מתאים ל**:[7]
- SaaS products
- web applications
- פרויקטים עם continuous deployment

***

**Gitflow (למוצרים מורכבים)**:[6][5][4]
```
main (production)
  ↓
develop (integration)
  ↓
feature/* (features)
release/* (pre-production)
hotfix/* (urgent fixes)
```

**מבנה**:[5][4]
- `main`: גרסת production בלבד
- `develop`: אינטגרציה של features
- `feature/*`: פיתוח תכונות
- `release/*`: הכנה לגרסה
- `hotfix/*`: תיקונים דחופים

**מתאים ל**:[5][7]
- מוצרים עם גרסאות מתוכננות
- צוותים גדולים (20+)
- תמיכה במספר גרסאות במקביל

***

#### 1.2 המלצה לפרויקט שלך

בהתבסס על בניית **מערכת מקומית של סוכנים וLLMs**, מומלץ על **Trunk-Based Development** עם שילוב של **GitHub Flow**:[7][5]

```bash
main (stable, deployed)
  ├── feature/agent-orchestration
  ├── feature/rag-implementation
  ├── fix/memory-leak-chromadb
  └── hotfix/critical-ollama-crash
```

**עקרונות**:
- שמור על `main` תמיד stable
- branches קצרים (1-3 ימים)
- CI/CD אוטומטי על כל PR
- Code review חובה לפני merge

***

### חלק 2: Conventional Commits וניהול גרסאות

#### 2.1 מבנה Commit Message

השתמש ב-**Conventional Commits** לאוטומציה של versioning:[8][9][10]

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types מרכזיים**:[9][8]
- `feat`: תכונה חדשה (→ MINOR bump)
- `fix`: תיקון באג (→ PATCH bump)
- `docs`: שינויי documentation
- `style`: עיצוב קוד (לא משפיע על לוגיקה)
- `refactor`: שינוי ארכיטקטוני
- `perf`: שיפור ביצועים
- `test`: הוספת/שיפור טסטים
- `chore`: תחזוקה (dependencies, configs)
- `ci`: שינויים ב-CI/CD
- `BREAKING CHANGE`: שינוי API (→ MAJOR bump)

**דוגמאות**:[10][8]
```bash
# תכונה חדשה
feat(agent): add multi-agent orchestration with LangGraph

# תיקון באג
fix(rag): resolve ChromaDB connection timeout

# שינוי breaking
feat(llm)!: change Ollama API endpoint structure

BREAKING CHANGE: endpoint now requires authentication token
```

#### 2.2 Semantic Versioning אוטומטי

השתמש ב-**semantic-release** או **Git Semantic Version Action**:[11][12][13]

```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: paulhatch/semantic-version@v5.4.0
        id: version
        with:
          tag_prefix: "v"
          major_pattern: "/(BREAKING CHANGE|!)/"
          minor_pattern: "/feat:/"
          version_format: "${major}.${minor}.${patch}"
      
      - name: Create Release
        if: steps.version.outputs.changed == 'true'
        run: |
          echo "New version: ${{ steps.version.outputs.version }}"
          gh release create v${{ steps.version.outputs.version }} \
            --title "Release ${{ steps.version.outputs.version }}" \
            --generate-notes
```

**תוצאה**:[13][11]
- `feat: ...` → v1.2.0 → v1.3.0
- `fix: ...` → v1.2.0 → v1.2.1
- `feat!: ...` → v1.2.0 → v2.0.0

***

### חלק 3: מבנה Repository (Monorepo vs Polyrepo)

#### 3.1 השוואה

| **קריטריון** | **Monorepo** | **Polyrepo** |
|--------------|--------------|--------------|
| **ארגון** | כל הקוד במקום אחד | repository לכל שירות |
| **שיתוף קוד** | קל מאוד | דורש packages |
| **CI/CD** | pipeline אחד מורכב | pipelines נפרדים |
| **גרסאות** | גרסה אחת לכל | עצמאות מלאה |
| **בעיות** | builds איטיים, גודל | תלויות מורכבות |

**מקורות**:[14][15][16][17][18]

#### 3.2 המלצה לפרויקט

**Monorepo** מומלץ למערכת שלך:[15][17][14]

```
project-root/
├── packages/
│   ├── agents/              # Multi-agent system
│   │   ├── orchestrator/
│   │   ├── executor/
│   │   └── retrieval/
│   ├── llm-interface/       # Ollama, DeepSeek, Llama
│   ├── rag-system/          # ChromaDB, embeddings
│   ├── ui/                  # Frontend (React/Vue)
│   └── shared/              # Utilities, types
├── tools/                   # Build scripts
├── .github/
│   └── workflows/
├── package.json             # Root config
└── README.md
```

**כלים מומלצים**:[14][15]
- **Nx**: orchestration חכם, caching
- **Turborepo**: builds מהירים
- **Lerna**: ניהול packages ב-JS/TS

**דוגמת Nx config**:
```json
{
  "projects": {
    "agents": "packages/agents",
    "llm-interface": "packages/llm-interface",
    "rag-system": "packages/rag-system"
  },
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "cache": true
    }
  }
}
```

***

### חלק 4: Pull Request Best Practices

#### 4.1 עקרונות מרכזיים

**1. PRs קטנים וממוקדים**:[19][20][21]
- מקסימום 400 שורות
- משימה אחת ברורה
- סיכוי גבוה יותר ל-approval מהיר

**2. תיאור מפורט**:[20][21][19]
```markdown
## תיאור
מוסיף orchestration layer למערכת הסוכנים עם LangGraph

## שינויים
- ✨ מחלקה `AgentOrchestrator` חדשה
- 🔧 אינטגרציה עם Ollama API
- ✅ טסטים ל-multi-agent coordination

## בדיקות
- [x] Unit tests עוברים
- [x] Integration tests עם Ollama local
- [x] Manual testing עם 3 agents במקביל

## Screenshots
![before-after](...)

## קישורים
Closes #123
Related to #124
```

**3. Self-review קודם**:[21][20]
- בדוק את הקוד שלך לפני PR
- הרץ linters
- וודא שהטסטים עוברים

**4. Labels וארגון**:[22][19]
```
🐛 bug
✨ feature
📝 documentation
🚀 performance
🔒 security
🧪 testing
```

#### 4.2 Code Review Guidelines

**למבצעי ה-PR**:[23][19][20]
- תגיב לכל comment
- היה פתוח לביקורת
- עדכן בזמן

**לreviewers**:[24][19][23]
- תן פידבק בונה
- התמקד בלוגיקה, לא בסגנון
- אשר תוך 24 שעות
- השתמש ב-suggestions:
  ```markdown
  ```
  const result = await fetchData();
  ```
  ```

**אוטומציה**:[19][20]
```yaml
# .github/workflows/pr-checks.yml
name: PR Checks
on: [pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm run lint
  
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test
  
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: github/codeql-action/analyze@v3
```

***

### חלק 5: GitHub Actions - CI/CD Security

#### 5.1 עקרונות אבטחה

**1. Secrets Management**:[25][26][27]
```yaml
jobs:
  deploy:
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.DEPLOY_API_KEY }}
        run: ./deploy.sh
```

- השתמש ב-GitHub Secrets
- אל תשמור credentials בקוד
- Rotate secrets תקופתית

**2. Pin Actions לSHA מלא**:[27][28][25]
```yaml
# ❌ רע
- uses: actions/checkout@v4

# ✅ טוב
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
```

**3. Least Privilege Permissions**:[28][25][27]
```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

**4. Code Scanning**:[26][20][27]
```yaml
- name: Run CodeQL
  uses: github/codeql-action/analyze@v3
  with:
    languages: python, javascript
```

#### 5.2 דוגמת Pipeline מאובטח

```yaml
name: Secure CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read
  security-events: write

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
      
      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
  
  build-and-test:
    needs: security-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11
      
      - name: Setup Node
        uses: actions/setup-node@60edb5dd545a775178f52524783378180af0d1f8
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test -- --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
  
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build-and-test
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy to production
        env:
          DEPLOY_KEY: ${{ secrets.PRODUCTION_DEPLOY_KEY }}
        run: ./scripts/deploy.sh
```

**מקורות**:[29][25][26][27][28]

***

### חלק 6: ניהול Issues ו-Projects

#### 6.1 שימוש ב-GitHub Issues

**מבנה Issue אידיאלי**:[1][22]
```markdown
## תיאור הבעיה
מערכת ה-RAG לא מצליחה להתחבר ל-ChromaDB לאחר 5 שניות

## שלבים לשחזור
1. הרץ `npm run start:rag`
2. שלח query עם מסמך גדול (>10MB)
3. המתן 5 שניות

## התנהגות מצופה
חיבור מוצלח תוך 3 שניות

## התנהגות בפועל
```
TimeoutError: ChromaDB connection failed after 5000ms
```

## סביבה
- OS: Ubuntu 22.04
- Node: v20.10.0
- ChromaDB: v0.4.18

## Logs
[attach logs]
```

**Labels מומלצים**:[22][1]
- `bug` / `feature` / `enhancement`
- `priority: high` / `medium` / `low`
- `status: in-progress` / `blocked` / `review`
- `area: agents` / `rag` / `ui`

**Automation**:[1]
```yaml
# .github/workflows/issue-triage.yml
name: Issue Triage
on:
  issues:
    types: [opened]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.addLabels({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              labels: ['triage']
            });
```

#### 6.2 GitHub Projects

**ארגון לוח**:[2][1]
```
Backlog → Todo → In Progress → Review → Done
```

**אוטומציה Built-in**:[2][1]
- העבר ל-"In Progress" כאשר branch נפתח
- העבר ל-"Review" כאשר PR נוצר
- העבר ל-"Done" כאשר PR נמזג

**Custom Fields**:[1]
- Priority (High/Med/Low)
- Effort (1-5)
- Sprint (Sprint 1, 2...)
- Owner (team member)

***

### חלק 7: Branch Protection Rules

#### 7.1 הגדרות מומלצות

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "ci/lint",
      "ci/test",
      "ci/security-scan"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true
  },
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

**CODEOWNERS file**:[3][30]
```
# .github/CODEOWNERS
* @team-leads

/packages/agents/ @agent-team
/packages/rag-system/ @rag-team
/packages/ui/ @frontend-team
*.md @docs-team
```

**מקורות**:[30][31][3][1]

***

### חלק 8: Backup וRecovery

#### 8.1 אסטרטגיות גיבוי

**1. Git History הוא הגיבוי**:[31][3]
- שמור commits ברורים
- אל תעשה force-push ל-main
- שמור tags לגרסאות

**2. GitHub Enterprise Backup**:[3]
```bash
# Backup automation
gh repo clone org/repo repo-backup-$(date +%Y%m%d)
tar -czf repo-backup-$(date +%Y%m%d).tar.gz repo-backup-*
aws s3 cp repo-backup-*.tar.gz s3://backups/
```

**3. Disaster Recovery Plan**:[30][3]
- גיבוי שבועי של הארגון
- גיבוי יומי של repositories קריטיים
- תרגול recovery תקופתי

***

### סיכום והמלצות סופיות

**לפרויקט בניית מערכת LLM מקומית**:

1. **Branching**: Trunk-Based עם GitHub Flow
2. **Commits**: Conventional Commits + Semantic Versioning
3. **Structure**: Monorepo עם Nx/Turborepo
4. **CI/CD**: GitHub Actions מאובטח עם scans
5. **Reviews**: PRs קטנים, 2 reviewers, אוטומציה
6. **Security**: Pin SHAs, secrets management, CodeQL
7. **Organization**: GitHub Projects + Issues + Labels
8. **Protection**: Branch rules + CODEOWNERS

**תוצאה**: פרויקט מאורגן, מאובטח, ניתן לתחזוקה ומדרגיות, עם תהליכי CI/CD מהירים ואמינים.

[1](https://docs.github.com/enterprise-cloud@latest/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects)
[2](https://github.blog/developer-skills/github/how-were-using-github-projects-to-standardize-our-workflows-and-stay-aligned/)
[3](https://graphite.dev/guides/github-enterprise-best-practices)
[4](https://docs.aws.amazon.com/prescriptive-guidance/latest/choosing-git-branch-approach/git-branching-strategies.html)
[5](https://www.getunleash.io/blog/how-to-implement-trunk-based-development-a-practical-guide)
[6](https://www.atlassian.com/continuous-delivery/continuous-integration/trunk-based-development)
[7](https://graphite.dev/guides/trunk-vs-gitflow)
[8](https://www.conventionalcommits.org/en/v1.0.0/)
[9](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)
[10](https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13)
[11](https://www.sei.cmu.edu/blog/versioning-with-git-tags-and-conventional-commits/)
[12](https://semantic-release.gitbook.io)
[13](https://github.com/marketplace/actions/git-semantic-version)
[14](https://www.aviator.co/blog/monorepo-a-hands-on-guide-for-managing-repositories-and-microservices/)
[15](https://circleci.com/blog/monorepo-dev-practices/)
[16](https://www.reddit.com/r/dotnet/comments/uaub7x/when_it_comes_to_microservices_do_you_put_each/)
[17](https://github.com/irahardianto/monorepo-microservices)
[18](https://www.gitkraken.com/blog/monorepo-vs-multi-repo-collaboration)
[19](https://devdynamics.ai/blog/pull-request-best-practices-in-2023/)
[20](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/helping-others-review-your-changes)
[21](https://blog.codacy.com/pull-request-best-practices)
[22](https://rewind.com/blog/best-practices-for-using-github-issues/)
[23](https://rewind.com/blog/best-practices-for-reviewing-pull-requests-in-github/)
[24](https://www.reddit.com/r/programming/comments/18mghkp/empirically_supported_code_review_best_practices/)
[25](https://www.linkedin.com/pulse/securing-your-cicd-pipeline-github-actions-best-practices-yeage)
[26](https://www.wiz.io/academy/ci-cd-security-best-practices)
[27](https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/)
[28](https://www.stepsecurity.io/blog/github-actions-security-best-practices)
[29](https://www.legitsecurity.com/blog/securing-your-ci/cd-pipeline-exploring-the-dangers-of-self-hosted-agents)
[30](https://wellarchitected.github.com/library/governance/recommendations/governance-policies-best-practices/)
[31](https://github.blog/enterprise-software/devops/best-practices-for-organizations-and-teams-using-github-enterprise-cloud/)
[32](https://github.com/orgs/community/discussions/171037)
[33](https://resources.github.com/learn/pathways/automation/advanced/enterprise-workflow-automation-at-scale/)
[34](https://www.zenhub.com/blog-posts/the-best-tools-for-github-enterprise-workflows-in-2025)
[35](https://www.toptal.com/software/trunk-based-development-git-flow)
[36](https://webstandards.ca.gov/2023/04/19/github-best-practices/)
[37](https://www.reddit.com/r/ExperiencedDevs/comments/1fitu38/advantages_of_standardized_commit_messages/)
[38](https://stackoverflow.com/questions/65855111/what-would-be-a-good-commit-message-for-updating-package-versions-using-conventi)
[39](https://docs.github.com/en/actions/reference/security/secure-use)
[40](https://www.conventionalcommits.org/en/v1.0.0-beta.2/)