# תוכנית פעולה - Zero Agent

**תאריך:** 26 באוקטובר 2025  
**מטרה:** התחלת פיתוח סוכנים + שיפורים נוספים

---

## 🎯 Phase 2: Agent System (יום 1-3)

### שלב 1: Agent Wrapper בסיסי
**קבצים:** `zero_agent/agent_orchestrator.py`

```python
class AgentOrchestrator:
    """מנהל סוכנים ומתאם משימות"""
    
    def __init__(self):
        self.task_planner = TaskPlanner()
        self.action_executor = ActionExecutor()
        self.safety_layer = SafetyLayer()
    
    def execute_goal(self, goal: str):
        """ביצוע מטרה מורכבת"""
        # 1. תכנן משימות
        tasks = self.task_planner.plan(goal)
        
        # 2. בצע עם מעקב
        for task in tasks:
            result = self.action_executor.execute(task)
            if not result.success:
                # תיקון טעיות
                self.handle_error(task, result)
```

**עדיפות:** 1  
**זמן משוער:** 4 שעות

---

### שלב 2: Task Planner
**קבצים:** `zero_agent/task_planner.py`

```python
class TaskPlanner:
    """תכנון משימות מורכבות לשלבים"""
    
    def plan(self, goal: str) -> List[Task]:
        """פירוק מטרה למשימות משנה"""
        # שימוש ב-LLM לפירוק
        prompt = f"פרק את המטרה הבאה לשלבים: {goal}"
        steps = self.llm.plan(prompt)
        return self.parse_steps(steps)
```

**עדיפות:** 2  
**זמן משוער:** 3 שעות

---

### שלב 3: Safety Layer
**קבצים:** `zero_agent/safety_layer.py`

```python
class SafetyLayer:
    """שכבת אבטחה לפעולות"""
    
    SAFE_ACTIONS = ['create_file', 'read_file', 'list_files']
    DANGEROUS_ACTIONS = ['delete', 'execute', 'install']
    
    def validate(self, action: Action) -> bool:
        """אישור פעולה"""
        if action.type in self.DANGEROUS_ACTIONS:
            return self.require_confirmation(action)
        return True
```

**עדיפות:** 3  
**זמן משוער:** 2 שעות

---

## 🚀 שיפורים נוספים

### 1. Real WebSocket Streaming
**סטטוס:** מוכן למימוש  
**זמן:** 3 שעות

- [ ] WebSocket handler ב-`api_server.py`
- [ ] Token-by-token streaming
- [ ] Progress indicators
- [ ] Stop mid-stream

---

### 2. RAG Integration
**סטטוס:** מחקר הושלם  
**זמן:** 5 שעות

- [ ] ChromaDB integration
- [ ] Document upload endpoint
- [ ] Citation in responses
- [ ] Source highlighting

---

### 3. Multi-Agent UI
**סטטוס:** נראה טוב  
**זמן:** 4 שעות

- [ ] Agent selector component
- [ ] Auto-routing indicators
- [ ] Parallel execution view
- [ ] Agent logs

---

### 4. Responsive Design
**סטטוס:** נחוץ  
**זמן:** 6 שעות

- [ ] Mobile optimization
- [ ] Tablet layout
- [ ] Collapsible sidebar
- [ ] Touch gestures

---

## 📋 סדר עדיפויות

### היום (שעות 1-4)
1. ✅ Agent Wrapper בסיסי
2. ✅ Task Planner
3. ✅ Safety Layer

### מחר (שעות 5-8)
4. WebSocket streaming
5. RAG בסיסי

### יום 3 (שעות 9-12)
6. Multi-Agent UI
7. Responsive Design

---

## 🎯 תוצאות צפויות

### Phase 2 - Agent System
- ✅ ביצוע פעולות מורכבות
- ✅ טיפול בטעיות אוטומטי
- ✅ אבטחה מובנית

### שיפורים נוספים
- ✅ Streaming בזמן אמת
- ✅ RAG עם מסמכים
- ✅ UI משופר ו-responsive

---

**סטטוס:** 🚀 מוכן להתחיל  
**Next:** התחלת מימוש Agent Wrapper

**Let's build! 🔨**
