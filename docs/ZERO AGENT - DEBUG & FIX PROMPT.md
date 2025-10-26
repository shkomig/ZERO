# 🔧 ZERO AGENT - DEBUG & FIX PROMPT

## 🎯 MISSION: תקן את Zero Agent בצורה מסודרת

אני צריך שתעשה debug מקצועי ומסודר למערכת Zero Agent. יש שגיאות שמונעות ריצה תקינה. תעבוד צעד אחר צעד, תתעד הכל, ותתקן.

---

## 📋 PHASE 1: DIAGNOSTIC (אבחון מלא)

### Step 1.1: בדוק את מבנה הפרויקט

```bash
# רשום את מבנה התיקיות הנוכחי
tree -L 3 zero_agent/

# או אם אין tree:
find zero_agent/ -type f -name "*.py" | head -20
```

**שאלות לענות עליהן:**
- ✅ כל התיקיות קיימות? (core/, models/, tools/, rag/, api/, ui/)
- ✅ כל הקבצים הראשיים קיימים?
- ✅ יש `__init__.py` בכל תיקייה?

---

### Step 1.2: בדוק Dependencies

```bash
# בדוק מה מותקן
pip list | grep -E "langgraph|langchain|anthropic|ollama|playwright"

# בדוק Python version
python --version

# בדוק אם Ollama רץ
curl http://localhost:11434/api/tags 2>/dev/null || echo "Ollama not running"
```

**רשום:**
- אילו packages חסרים?
- האם Python 3.11+?
- האם Ollama פעיל?

---

### Step 1.3: נסה להריץ ותעד שגיאות

```bash
# נסה להריץ
cd zero_agent
python main.py 2>&1 | tee error_log.txt
```

**תעד את כל השגיאות:**
```
ERROR 1: [שם השגיאה]
File: [איזה קובץ]
Line: [שורה]
Message: [הודעת שגיאה מלאה]

ERROR 2: ...
```

---

### Step 1.4: בדוק imports

צור קובץ: `test_imports.py`

```python
"""
Test all critical imports
"""
import sys

def test_import(module_name, package=None):
    try:
        if package:
            exec(f"from {package} import {module_name}")
        else:
            exec(f"import {module_name}")
        print(f"✅ {package or module_name}.{module_name if package else ''}")
        return True
    except ImportError as e:
        print(f"❌ {package or module_name}.{module_name if package else ''}")
        print(f"   Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️ {package or module_name}.{module_name if package else ''}")
        print(f"   Error: {e}")
        return False

print("Testing Critical Imports:\n")

# Core dependencies
test_import("langgraph")
test_import("langchain")
test_import("langchain_anthropic")
test_import("anthropic")
test_import("ollama")

# Tools
test_import("playwright")
test_import("playwright.async_api", "playwright")
test_import("docker")
test_import("gitpython")

# Data
test_import("chromadb")
test_import("redis")
test_import("sentence_transformers")

# System
test_import("psutil")
test_import("pydantic")
test_import("fastapi")

print("\n" + "="*50)
print("Import Test Complete")
```

הרץ: `python test_imports.py`

---

## 📋 PHASE 2: MINIMAL WORKING VERSION

**המטרה:** בנה גרסה מינימלית שרצה בלי שגיאות, אפילו בלי כל הפיצ'רים.

### Step 2.1: צור `main_minimal.py`

```python
"""
Minimal working version of Zero Agent
Test basic functionality only
"""

import asyncio
from pathlib import Path

print("🤖 Zero Agent - Minimal Test")
print("="*50)

# Test 1: Basic imports
print("\n1. Testing imports...")
try:
    from langchain_anthropic import ChatAnthropic
    print("   ✅ LangChain imports OK")
except Exception as e:
    print(f"   ❌ LangChain import failed: {e}")
    exit(1)

try:
    import ollama
    print("   ✅ Ollama import OK")
except Exception as e:
    print(f"   ❌ Ollama import failed: {e}")
    exit(1)

# Test 2: Ollama connection
print("\n2. Testing Ollama connection...")
try:
    client = ollama.Client()
    models = client.list()
    print(f"   ✅ Ollama connected. Models: {len(models.get('models', []))}")
except Exception as e:
    print(f"   ❌ Ollama connection failed: {e}")
    print("   💡 Start Ollama: 'ollama serve'")
    exit(1)

# Test 3: Simple model call
print("\n3. Testing model call...")
try:
    response = client.chat(
        model='llama3.1:8b',
        messages=[{'role': 'user', 'content': 'Say "OK" only'}]
    )
    result = response['message']['content']
    print(f"   ✅ Model responded: {result[:50]}")
except Exception as e:
    print(f"   ❌ Model call failed: {e}")
    print("   💡 Pull model: 'ollama pull llama3.1:8b'")

# Test 4: File system
print("\n4. Testing file system...")
try:
    workspace = Path("./workspace")
    workspace.mkdir(exist_ok=True)
    test_file = workspace / "test.txt"
    test_file.write_text("test")
    assert test_file.read_text() == "test"
    test_file.unlink()
    print("   ✅ File system OK")
except Exception as e:
    print(f"   ❌ File system failed: {e}")

print("\n" + "="*50)
print("✅ Minimal test complete!")
print("\nIf all tests passed, we can proceed to full system.")
```

**הרץ:** `python main_minimal.py`

**אם יש שגיאות - תקן אותן לפני שממשיכים!**

---

### Step 2.2: צור `config_simple.py`

```python
"""
Simple configuration - no external dependencies
"""
from pathlib import Path
from typing import Dict, Any
import os

class SimpleConfig:
    """Simple configuration without yaml/external files"""
    
    # Paths
    BASE_DIR = Path(__file__).parent
    WORKSPACE_DIR = BASE_DIR / "workspace"
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Ollama
    OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # Models (only those that exist)
    AVAILABLE_MODELS = {
        "fast": "llama3.1:8b",
        "reasoning": "deepseek-r1:32b",
        "coding": "qwen2.5-coder:32b"
    }
    
    # API Keys (optional)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    @classmethod
    def setup(cls):
        """Create necessary directories"""
        cls.WORKSPACE_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def get_model(cls, task_type: str = "fast") -> str:
        """Get model for task type"""
        return cls.AVAILABLE_MODELS.get(task_type, cls.AVAILABLE_MODELS["fast"])

# Setup on import
SimpleConfig.setup()
```

---

### Step 2.3: צור `orchestrator_simple.py`

```python
"""
Simple orchestrator - no LangGraph, just basic flow
"""

import asyncio
import ollama
from typing import Dict, Any
from config_simple import SimpleConfig

class SimpleOrchestrator:
    """Simple task orchestrator without complex dependencies"""
    
    def __init__(self):
        self.ollama_client = ollama.Client(host=SimpleConfig.OLLAMA_HOST)
        print("✅ SimpleOrchestrator initialized")
    
    async def execute(self, task: str) -> Dict[str, Any]:
        """Execute a simple task"""
        
        print(f"\n🎯 Task: {task}")
        
        # Step 1: Understand task
        print("📝 Understanding task...")
        understanding = await self._understand_task(task)
        
        # Step 2: Execute
        print("⚙️ Executing...")
        result = await self._execute_task(understanding)
        
        print("✅ Done!")
        
        return {
            "task": task,
            "understanding": understanding,
            "result": result,
            "success": True
        }
    
    async def _understand_task(self, task: str) -> str:
        """Understand what user wants"""
        
        model = SimpleConfig.get_model("fast")
        
        try:
            response = self.ollama_client.chat(
                model=model,
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful assistant. Analyze the task briefly.'
                    },
                    {
                        'role': 'user',
                        'content': f'Task: {task}\n\nWhat does the user want? Answer in 1 sentence.'
                    }
                ]
            )
            
            return response['message']['content']
            
        except Exception as e:
            print(f"⚠️ Understanding failed: {e}")
            return "Could not understand task"
    
    async def _execute_task(self, understanding: str) -> str:
        """Execute the task"""
        
        # For now, just return the understanding
        # Later we'll add actual execution
        return f"Understood: {understanding}"

# Test
async def test_orchestrator():
    """Test the simple orchestrator"""
    
    orch = SimpleOrchestrator()
    
    # Test simple task
    result = await orch.execute("Say hello")
    
    print("\n" + "="*50)
    print("Result:")
    print(f"  Task: {result['task']}")
    print(f"  Understanding: {result['understanding']}")
    print(f"  Result: {result['result']}")
    print(f"  Success: {result['success']}")

if __name__ == "__main__":
    print("Testing SimpleOrchestrator...\n")
    asyncio.run(test_orchestrator())
```

**הרץ:** `python orchestrator_simple.py`

---

### Step 2.4: צור `main_working.py`

```python
"""
Working main.py with simple orchestrator
"""

import asyncio
from orchestrator_simple import SimpleOrchestrator
from config_simple import SimpleConfig

async def main():
    """Main entry point"""
    
    print("🤖 Zero Agent - Simple Version")
    print("="*50)
    print(f"Workspace: {SimpleConfig.WORKSPACE_DIR}")
    print(f"Ollama: {SimpleConfig.OLLAMA_HOST}")
    print("="*50)
    
    # Initialize orchestrator
    orchestrator = SimpleOrchestrator()
    
    print("\n✅ Zero Agent ready!\n")
    
    # Interactive loop
    while True:
        try:
            task = input("Zero> ").strip()
            
            if not task:
                continue
            
            if task.lower() in ['exit', 'quit', 'q']:
                print("👋 Goodbye!")
                break
            
            # Execute task
            result = await orchestrator.execute(task)
            
            print(f"\n💬 {result['result']}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
```

**הרץ:** `python main_working.py`

---

## 📋 PHASE 3: SYSTEMATIC FIX

אם הגרסה הפשוטה עובדת, עכשיו תקן את הגרסה המלאה:

### Step 3.1: תקן Imports

בכל קובץ שיש בו שגיאת import:

```python
# Before (broken):
from langchain.something import Something

# After (fixed):
try:
    from langchain.something import Something
except ImportError:
    from langchain_community.something import Something
```

### Step 3.2: תקן Type Hints

```python
# Before (might cause issues):
from typing import Annotated, Sequence

# After (safe):
from typing import Annotated, Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from langgraph.graph import StateGraph
```

### Step 3.3: תקן Async/Await

```python
# Common mistake:
def some_function():
    result = await some_async_function()  # ❌ await outside async

# Fix:
async def some_function():
    result = await some_async_function()  # ✅
```

### Step 3.4: תקן Environment Variables

```python
# Before (crashes if missing):
api_key = os.environ["ANTHROPIC_API_KEY"]

# After (safe):
api_key = os.getenv("ANTHROPIC_API_KEY", "")
if not api_key and need_api:
    raise ValueError("ANTHROPIC_API_KEY not set")
```

---

## 📋 PHASE 4: GRADUAL INTEGRATION

עכשיו שהגרסה הפשוטה עובדת, הוסף פיצ'רים אחד אחד:

### Step 4.1: הוסף Model Router

```python
# Create: models/router_fixed.py
# Copy from orchestrator_simple.py and extend
```

### Step 4.2: הוסף Tools

```python
# Start with one tool
# tools/system_simple.py - just CPU check
# Test it works
# Add more tools
```

### Step 4.3: הוסף LangGraph

```python
# Only after everything else works
# models/orchestrator_langgraph.py
```

---

## 📋 PHASE 5: CREATE FIX REPORT

צור קובץ: `FIX_REPORT.md`

```markdown
# Zero Agent - Fix Report

## Issues Found

### Issue 1: [Name]
**Error:** [exact error message]
**File:** [file:line]
**Cause:** [what caused it]
**Fix:** [what you did]
**Status:** ✅ Fixed / ⚠️ Partial / ❌ Blocked

### Issue 2: ...

## Working Features
- ✅ Feature 1
- ✅ Feature 2
- ⚠️ Feature 3 (partial)
- ❌ Feature 4 (not working)

## Next Steps
1. [what to do next]
2. [...]

## Files Modified
- `core/orchestrator.py` - [changes]
- `models/router.py` - [changes]

## How to Test
```bash
# Test commands
python main_working.py
```

## Notes
[any important notes]
```

---

## 🎯 EXECUTION CHECKLIST

עבור בסדר הזה - אל תדלג!

```markdown
□ Phase 1: Diagnostic
  □ Step 1.1: מבנה פרויקט
  □ Step 1.2: Dependencies
  □ Step 1.3: הרצה + שגיאות
  □ Step 1.4: בדיקת imports

□ Phase 2: Minimal Version
  □ Step 2.1: main_minimal.py
  □ Step 2.2: config_simple.py
  □ Step 2.3: orchestrator_simple.py
  □ Step 2.4: main_working.py

□ Phase 3: Systematic Fix
  □ Step 3.1: תיקון imports
  □ Step 3.2: תיקון type hints
  □ Step 3.3: תיקון async/await
  □ Step 3.4: תיקון env vars

□ Phase 4: Gradual Integration
  □ Step 4.1: Model router
  □ Step 4.2: Tools
  □ Step 4.3: LangGraph

□ Phase 5: Documentation
  □ FIX_REPORT.md
  □ Update README.md
```

---

## 🆘 IF STUCK

### אם Phase 1 נכשל:
```bash
# Reinstall everything
pip uninstall -y langgraph langchain langchain-anthropic
pip install langgraph langchain langchain-anthropic anthropic

# Check Ollama
ollama list
ollama pull llama3.1:8b
```

### אם Phase 2 נכשל:
```
Stop here!
Show me the error from main_minimal.py
I'll help debug specifically
```

### אם Phase 3 נכשל:
```
Fix one file at a time
Test after each fix
Don't move on until it works
```

---

## 💡 DEBUG TIPS

1. **הוסף prints בכל מקום:**
```python
print(f"DEBUG: Entering function X")
print(f"DEBUG: Variable Y = {y}")
print(f"DEBUG: About to call Z")
```

2. **השתמש ב-try/except:**
```python
try:
    result = risky_function()
except Exception as e:
    print(f"ERROR in risky_function: {e}")
    print(f"Type: {type(e)}")
    import traceback
    traceback.print_exc()
```

3. **בדוק צעד אחר צעד:**
```python
# Don't do:
result = function1(function2(function3()))

# Do:
temp1 = function3()
print(f"After function3: {temp1}")
temp2 = function2(temp1)
print(f"After function2: {temp2}")
result = function1(temp2)
print(f"After function1: {result}")
```

---

## 🎯 SUCCESS CRITERIA

**הצלחת כש:**
1. ✅ `main_minimal.py` רץ בלי שגיאות
2. ✅ `main_working.py` רץ ומקבל input
3. ✅ Zero מגיב לפקודות בסיסיות
4. ✅ אין import errors
5. ✅ Ollama מחובר ועובד

**אז תוכל להתחיל להוסיף פיצ'רים מתקדמים!**

---

## 📝 FINAL INSTRUCTIONS FOR CURSOR

```
Dear Cursor,

Please follow this document EXACTLY in order:
1. Start with Phase 1 - Diagnostic
2. Create all the simple versions in Phase 2
3. Only proceed to Phase 3 after Phase 2 works
4. Document everything in FIX_REPORT.md

Be methodical. Be patient. Test after every change.

When done, show me:
1. FIX_REPORT.md
2. Output from main_working.py
3. List of what works and what doesn't

Thank you!
```

---

**Good luck! ביצוע מסודר = הצלחה! 🚀**