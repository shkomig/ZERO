"""
Agent Orchestrator - מנהל סוכנים ומתאם משימות מורכבות
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """משימה לביצוע"""
    id: str
    description: str
    action_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # IDs של משימות תלויות
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """תוצאה של ביצוע פעולה"""
    success: bool
    output: Any
    error: Optional[str] = None
    duration: float = 0.0


class AgentOrchestrator:
    """
    מנהל סוכנים ומתאם משימות מורכבות
    
    תפקידים:
    1. פירוק מטרות מורכבות למשימות משנה
    2. ניהול ביצוע רצף משימות
    3. טיפול בטעיות ושחזור
    4. מעקב אחר התקדמות
    """
    
    def __init__(self, llm, tools):
        """
        Initialize the orchestrator
        
        Args:
            llm: LLM instance for planning
            tools: Dictionary of available tools
        """
        self.llm = llm
        self.tools = tools
        self.tasks: Dict[str, Task] = {}
        self.execution_log: List[Dict[str, Any]] = []
        
    def execute_goal(self, goal: str, max_iterations: int = 10) -> ExecutionResult:
        """
        ביצוע מטרה מורכבת
        
        Args:
            goal: המטרה לביצוע
            max_iterations: מקסימום איטרציות
            
        Returns:
            ExecutionResult עם תוצאה
        """
        logger.info(f"🎯 Starting goal execution: {goal}")
        
        try:
            # 1. תכנן משימות
            tasks = self._plan_tasks(goal)
            logger.info(f"📋 Planned {len(tasks)} tasks")
            
            # 2. בצע משימות
            for iteration in range(max_iterations):
                # מצא משימות שמוכנות לביצוע
                ready_tasks = self._get_ready_tasks()
                
                if not ready_tasks:
                    # אין משימות מוכנות
                    if all(t.status in ['completed', 'failed'] for t in tasks):
                        # כל המשימות הושלמו
                        break
                    else:
                        # יש משימות אך לא מוכנות (תלויות באחרות)
                        continue
                
                # בצע משימות מוכנות
                for task in ready_tasks:
                    result = self._execute_task(task)
                    
                    # עדכון סטטוס
                    task.status = 'completed' if result.success else 'failed'
                    task.result = result.output
                    task.error = result.error
                    
                    logger.info(f"{'✅' if result.success else '❌'} Task {task.id}: {task.description}")
                    
                    # לוג ביצוע
                    self.execution_log.append({
                        'task_id': task.id,
                        'success': result.success,
                        'duration': result.duration,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # אם נכשל, נסה לשחזר
                    if not result.success:
                        self._handle_error(task, result)
                        break
            
            # 3. החזר תוצאה
            return self._create_final_result(tasks)
            
        except Exception as e:
            logger.error(f"❌ Error in goal execution: {str(e)}")
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e)
            )
    
    def _plan_tasks(self, goal: str) -> List[Task]:
        """
        תכנון משימות - פירוק מטרה למשימות משנה
        
        Args:
            goal: המטרה
            
        Returns:
            רשימת משימות
        """
        # TODO: Use LLM for intelligent task planning
        # For now, use simple heuristic-based planning
        
        # זהה סוג המשימה
        goal_lower = goal.lower()
        
        tasks = []
        
        # דוגמה: יצירת פרויקט חדש
        if 'צור פרויקט' in goal or 'create project' in goal or 'פרויקט' in goal:
            # Extract project name from goal
            project_name = "myapp"  # default
            for word in goal.split():
                if word not in ['צור', 'פרויקט', 'create', 'project', 'חדש', 'בשם', 'new', 'named', 'called']:
                    project_name = word
                    break
            
            tasks.append(Task(
                id="1",
                description=f"Create project directory: {project_name}",
                action_type="create_folder",
                parameters={"path": f"./{project_name}"}
            ))
            tasks.append(Task(
                id="2",
                description="Create README file",
                action_type="create_file",
                parameters={"path": f"./{project_name}/README.md", "content": f"# {project_name}\n\nPython project"},
                dependencies=["1"]
            ))
            tasks.append(Task(
                id="3",
                description="Create main.py",
                action_type="create_file",
                parameters={"path": f"./{project_name}/main.py", "content": "#!/usr/bin/env python3\n\nprint('Hello, world!')\n"},
                dependencies=["1"]
            ))
        
        # דוגמה: חיפוש ברשת
        elif 'חפש' in goal or 'search' in goal:
            tasks.append(Task(
                id="1",
                description="Search the web",
                action_type="web_search",
                parameters={"query": goal}
            ))
        
        # אחרת - משימה פשוטה
        else:
            tasks.append(Task(
                id="1",
                description=goal,
                action_type="custom",
                parameters={"goal": goal}
            ))
        
        # שמירה ברשימה
        for task in tasks:
            self.tasks[task.id] = task
        
        return tasks
    
    def _get_ready_tasks(self) -> List[Task]:
        """
        החזר משימות שמוכנות לביצוע (כל ה-depencies הושלמו)
        
        Returns:
            רשימת משימות מוכנות
        """
        ready_tasks = []
        
        for task in self.tasks.values():
            if task.status != 'pending':
                continue
            
            # בדוק אם כל ה-dependencies הושלמו
            all_deps_completed = all(
                self.tasks[dep_id].status == 'completed'
                for dep_id in task.dependencies
            )
            
            if all_deps_completed:
                ready_tasks.append(task)
        
        return ready_tasks
    
    def _execute_task(self, task: Task) -> ExecutionResult:
        """
        ביצוע משימה אחת
        
        Args:
            task: המשימה
            
        Returns:
            ExecutionResult
        """
        from time import time
        start_time = time()
        
        task.status = 'in_progress'
        logger.info(f"⚙️ Executing task {task.id}: {task.description}")
        
        try:
            # בדוק אם יש tool מתאים
            logger.info(f"Checking tools for action_type: {task.action_type}")
            logger.info(f"Available tools: {list(self.tools.keys())}")
            
            if task.action_type in self.tools:
                tool = self.tools[task.action_type]
                
                # בצע את הפעולה - יכול להיות method או execute
                if hasattr(tool, task.action_type):
                    # יש method עם השם הזה (למשל create_folder)
                    method = getattr(tool, task.action_type)
                    result = method(**task.parameters)
                    logger.info(f"Tool method '{task.action_type}' executed: {result}")
                elif hasattr(tool, 'execute'):
                    # יש method execute גנרית
                    result = tool.execute(**task.parameters)
                    logger.info(f"Tool execute executed: {result}")
                else:
                    # אין method מתאים
                    logger.warning(f"Tool has no method '{task.action_type}' or 'execute'")
                    result = {"success": False, "error": "No suitable method found"}
                
                duration = time() - start_time
                
                # Check if result indicates success
                task_success = result.get("success", True) if isinstance(result, dict) else True
                
                return ExecutionResult(
                    success=task_success,
                    output=result,
                    duration=duration
                )
            else:
                # אין tool מתאים - נסה דרך LLM
                logger.warning(f"No tool found for {task.action_type}, using LLM")
                
                # TODO: Use LLM to execute the task
                result = "Task executed via LLM"
                
                duration = time() - start_time
                
                return ExecutionResult(
                    success=True,
                    output=result,
                    duration=duration
                )
                
        except Exception as e:
            duration = time() - start_time
            logger.error(f"Error executing task {task.id}: {str(e)}")
            
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e),
                duration=duration
            )
    
    def _handle_error(self, task: Task, result: ExecutionResult):
        """
        טיפול בטעיות - ניסיון לשחזר
        
        Args:
            task: המשימה שנכשלה
            result: התוצאה הכושלת
        """
        logger.warning(f"⚠️ Task {task.id} failed: {result.error}")
        
        # TODO: Implement error recovery logic
        # - Retry with different parameters
        # - Fallback to alternative approach
        # - Request human intervention if critical
        
        pass
    
    def _create_final_result(self, tasks: List[Task]) -> ExecutionResult:
        """
        יצירת תוצאה סופית מהמשימות
        
        Args:
            tasks: כל המשימות
            
        Returns:
            ExecutionResult סופי
        """
        # ספירת משימות
        completed = sum(1 for t in tasks if t.status == 'completed')
        failed = sum(1 for t in tasks if t.status == 'failed')
        
        # החזר תוצאה
        if failed == 0:
            # כל המשימות הצליחו
            return ExecutionResult(
                success=True,
                output=f"Successfully completed {completed} tasks"
            )
        else:
            # חלק מהמשימות נכשלו
            return ExecutionResult(
                success=False,
                output=f"Completed {completed}/{len(tasks)} tasks",
                error=f"{failed} tasks failed"
            )
    
    def get_status(self) -> Dict[str, Any]:
        """
        החזר סטטוס נוכחי של ההרצה
        
        Returns:
            Dictionary עם מידע על סטטוס
        """
        return {
            'total_tasks': len(self.tasks),
            'completed': sum(1 for t in self.tasks.values() if t.status == 'completed'),
            'failed': sum(1 for t in self.tasks.values() if t.status == 'failed'),
            'in_progress': sum(1 for t in self.tasks.values() if t.status == 'in_progress'),
            'pending': sum(1 for t in self.tasks.values() if t.status == 'pending'),
            'execution_log': self.execution_log
        }
