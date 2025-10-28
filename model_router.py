"""
Model Router
============
Analyzes tasks and automatically selects the best model
"""

from typing import Dict, Any, Optional


class ModelRouter:
    """
    Smart router that analyzes task and selects optimal model
    """
    
    # Keywords for model selection (UPGRADED FOR SMART ROUTING!)
    KEYWORDS = {
        "coder": [
            # English - CODE GENERATION
            "write code", "write a function", "write a script", 
            "debug this code", "fix this code", "refactor code", 
            "optimize code", "code review", "implement", 
            "create a class", "create a function", "build app",
            "create api", "build", "develop", "program",
            # Hebrew - CODE GENERATION
            "כתוב קוד", "כתוב פונקציה", "בנה פונקציה", 
            "תקן את הקוד", "תכנת", "תבנה אפליקציה", 
            "תבנה מערכת", "פתח", "צור אפליקציה", 
            "צור מערכת", "צור פרויקט", "בנה פרויקט",
            "יצור קוד", "כתיבת קוד", "סקריפט ש", "פונקציה ש"
        ],
        "hebrew": [
            # Hebrew text/explanation tasks - HIGH PRIORITY
            "ספר לי", "הסבר", "מה זה", "מהו", "מהי",
            "תאר", "תיאור", "מושג", "רעיון", "הגדרה",
            "איך", "למה", "מתי", "היסטוריה", 
            "דוגמה", "דוגמאות", "דוגמאות ל",
            "ראשי פרקים", "נושאים", "סעיפים", 
            "פירוט", "מפורט", "תרגום", "מילים", "משפט"
        ],
        "smart": [
            # Complex reasoning
            "analyze deeply", "explain in detail", "philosophy", 
            "complex reasoning", "think step by step", 
            "detailed analysis", "comprehensive", "evaluate",
            "compare thoroughly", "research", "deep dive", 
            "critical thinking", "elaborate", "nuanced", 
            "sophisticated", "intricate", "נתח", "השווה"
        ]
    }
    
    def __init__(self, llm):
        self.llm = llm
        self.use_smart_routing = True
        
    def route(self, task: str, force_model: Optional[str] = None) -> str:
        """
        Analyze task and return best model
        
        Args:
            task: The task/prompt
            force_model: Force specific model (overrides routing)
            
        Returns:
            Model type: "fast", "coder", "smart", or "balanced"
        """
        if force_model:
            return force_model
        
        if not self.use_smart_routing:
            return "fast"  # Default
        
        task_lower = task.lower()
        
        # Score each model type (UPDATED WITH HEBREW!)
        scores = {
            "hebrew": 0,    # Mistral - for Hebrew explanations
            "coder": 0,     # qwen2.5-coder - for code generation
            "smart": 0,     # deepseek-r1 - for deep reasoning
            "balanced": 0   # fallback
        }
        
        # STEP 1: Check for EXPLANATION keywords first (HIGH PRIORITY)
        explanation_triggers = [
            "מה זה", "מהו", "מהי", "הסבר", "ספר לי",
            "what is", "explain"
        ]
        is_explanation = any(
            trigger in task_lower for trigger in explanation_triggers
        )
        
        if is_explanation:
            scores["hebrew"] += 5  # Strong boost for explanations
        
        # STEP 2: Check for CODE GENERATION keywords
        code_action_words = [
            "תבנה", "צור", "כתוב", "בנה", "פתח", "קוד",
            "תן לי קוד", "כתוב לי קוד", "הראה לי קוד",
            "write code", "give me code", "show me code",
            "build app", "create", "implement"
        ]
        is_code_generation = any(
            action in task_lower for action in code_action_words
        )
        
        # Extra boost if "קוד" or "code" appears explicitly
        if "קוד" in task_lower or "code" in task_lower:
            scores["coder"] += 3
        
        if is_code_generation:
            scores["coder"] += 5  # Strong boost for code generation
        
        # STEP 3: Check for actual code syntax (VERY STRONG INDICATOR)
        code_indicators = [
            "```", "def ", "class ", "import ",
            "function", "return", ".py", ".js"
        ]
        for indicator in code_indicators:
            if indicator in task_lower:
                scores["coder"] += 10  # VERY strong boost for actual code
        
        # STEP 4: General keyword matching
        for model_type, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if keyword in task_lower:
                    scores[model_type] += 1
        
        # STEP 5: Detect Hebrew text (baseline)
        has_hebrew = any('\u0590' <= char <= '\u05FF' for char in task)
        if has_hebrew and not is_code_generation:
            scores["hebrew"] += 1  # Mild boost for Hebrew text
        
        # STEP 6: Short math/simple questions -> hebrew (fast)
        if (len(task) < 15 and
                any(char in task for char in "0123456789+-*/=")):
            scores["hebrew"] += 2
        
        # Length-based heuristics
        word_count = len(task.split())
        
        if word_count < 10 and scores["coder"] == 0:
            scores["hebrew"] += 1  # Short Hebrew queries
        elif word_count > 30:
            scores["smart"] += 1
        
        # Get highest scoring model
        best_model = max(scores.items(), key=lambda x: x[1])
        
        # If no clear winner (all zeros), default to hebrew for Hebrew
        # text or smart otherwise
        if best_model[1] == 0:
            if has_hebrew:
                return "hebrew"
            return "smart"  # Default for generic tasks
        
        # If tie, prefer: coder > hebrew > smart > balanced
        if list(scores.values()).count(best_model[1]) > 1:
            if scores["coder"] == best_model[1]:
                return "coder"
            elif scores["hebrew"] == best_model[1]:
                return "hebrew"
            elif scores["smart"] == best_model[1]:
                return "smart"
        
        return best_model[0]
    
    def route_with_reasoning(self, task: str) -> Dict[str, Any]:
        """
        Route with explanation of choice
        
        Returns:
            {
                "model": "fast/coder/smart/balanced",
                "reasoning": "Why this model was chosen",
                "confidence": 0.0-1.0
            }
        """
        model = self.route(task)
        
        task_lower = task.lower()
        reasons = []
        
        # Explain decision
        if model == "coder":
            coder_kw = ["write code", "debug", "implement"]
            if any(kw in task_lower for kw in coder_kw):
                reasons.append("Task involves coding")
            if any(pattern in task for pattern in ['```', 'def ', 'class ']):
                reasons.append("Contains code syntax")
            confidence = 0.9
            
        elif model == "smart":
            smart_kw = ["analyze", "explain deeply", "complex"]
            if any(kw in task_lower for kw in smart_kw):
                reasons.append("Requires deep analysis")
            if len(task.split()) > 30:
                reasons.append("Long, detailed task")
            confidence = 0.85
            
        elif model == "fast":
            if len(task.split()) < 10:
                reasons.append("Short, simple query")
            if task.count('?') == 1:
                reasons.append("Single question")
            confidence = 0.8
            
        else:  # balanced
            reasons.append("General task, balanced approach")
            confidence = 0.7
        
        reasoning = " | ".join(reasons) if reasons else "Default choice"
        
        return {
            "model": model,
            "reasoning": reasoning,
            "confidence": confidence
        }
    
    def explain_routing(self, task: str):
        """
        Print detailed explanation of routing decision
        """
        result = self.route_with_reasoning(task)
        
        print("\n" + "=" * 70)
        print("ROUTING DECISION")
        print("=" * 70)
        print(f"\nTask: {task[:100]}...")
        print(f"\nSelected Model: {result['model'].upper()}")
        print(f"Confidence: {result['confidence'] * 100:.0f}%")
        print(f"Reasoning: {result['reasoning']}")
        
        model_info = self.llm.MODELS[result['model']]
        print(f"\nModel Details:")
        print(f"  Name: {model_info['name']}")
        print(f"  Speed: {model_info['speed']}")
        print(f"  Quality: {model_info['quality']}")
        print("=" * 70 + "\n")
    
    def enable_smart_routing(self):
        """Enable automatic model selection"""
        self.use_smart_routing = True
        print("✓ Smart routing enabled")
    
    def disable_smart_routing(self):
        """Disable automatic model selection (use default)"""
        self.use_smart_routing = False
        print("✓ Smart routing disabled - using default model")


# Test
if __name__ == "__main__":
    from multi_model_llm import MultiModelLLM
    
    print("Model Router Test")
    print("=" * 70)
    
    llm = MultiModelLLM()
    router = ModelRouter(llm)
    
    # Test cases
    test_tasks = [
        "What is 2+2?",
        "Write a Python function to calculate fibonacci numbers",
        "Analyze the philosophical implications of artificial intelligence on human consciousness",
        "Debug this code: def hello() print('hi')",
        "Explain quantum computing in simple terms",
        "Create a React component for a login form",
        "Compare and contrast different machine learning algorithms in detail"
    ]
    
    print("\nTesting routing for different tasks:\n")
    
    for task in test_tasks:
        result = router.route_with_reasoning(task)
        print(f"Task: {task[:60]}...")
        model = result['model'].upper()
        conf = result['confidence'] * 100
        print(f"  -> Model: {model} ({conf:.0f}% confidence)")
        print(f"  -> Reason: {result['reasoning']}")
        print()
    
    print("=" * 70)
    print("Router is smart and ready!")
