"""
Model Router
============
Analyzes tasks and automatically selects the best model
"""

import re
from typing import Dict, Any, Optional


class ModelRouter:
    """
    Smart router that analyzes task and selects optimal model
    """
    
    # Keywords for model selection (updated with Mixtral 8x7B)
    KEYWORDS = {
        "expert": [
            "advanced", "complex", "sophisticated", "expert", "professional",
            "comprehensive", "detailed analysis", "multi-step", "intricate",
            "advanced reasoning", "expert level", "professional grade",
            "מתקדם", "מורכב", "מקצועי", "מומחה", "מעמיק",
            "שלב אחר שלב", "צעד אחר צעד", "חלון", "חלונות",
            "קומה", "קומות", "רגליים", "נתונים מסיחים",
            "הצג את החישוב", "היגיון", "מכתב", "התפטרות", "נוסח"
        ],
        "coder": [
            "write code", "write a function", "write a script", "debug this code",
            "fix this code", "refactor code", "optimize code", "code review",
            "implement", "create a class", "create a function", "כתוב קוד",
            "בנה פונקציה", "תקן את הקוד", "צור קוד", "פיתוח", "programming",
            "algorithm"
        ],
        "smart": [
            "analyze deeply", "explain in detail", "philosophy", "complex reasoning",
            "think step by step", "detailed analysis", "comprehensive", "evaluate",
            "compare thoroughly", "research", "deep dive", "critical thinking",
            "elaborate", "nuanced", "sophisticated", "intricate", "אסטרטגיה",
            "ניתוח מעמיק", "חשיבה ביקורתית"
        ],
        "fast": [
            "quick", "simple", "what is", "מה זה", "convert", "translate",
            "define", "summarize", "list", "count", "basic", "easy", "explain",
            "?", "מתי", "פתח", "צור", "בדוק"
        ]
    }
    LOGIC_KEYWORDS = [
        "שלב אחר שלב", "צעד אחר צעד", "הצג את החישוב", "נתונים מסיחים",
        "חלון", "חלונות", "קומה", "קומות", "רגליים", "חידה לוגית",
        "logical puzzle", "show your work", "מכתב", "נוסח", "התפטרות"
    ]
    
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
            return "expert"  # Default
        
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in self.LOGIC_KEYWORDS):
            return "expert"

        # Score each model type
        scores = {
            "fast": 0,
            "expert": 0,
            "coder": 0,
            "smart": 0,
            "balanced": 0
        }
        
        # Check keywords
        for model_type, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if keyword in task_lower:
                    scores[model_type] += 1
        
        # Length-based heuristics
        word_count = len(task.split())
        
        if word_count < 10:
            scores["fast"] += 2
        elif word_count > 30:
            scores["smart"] += 2
        
        # Code-specific patterns (only actual code blocks)
        if any(pattern in task for pattern in ['```', 'def ', 'class ', 'import ', '()\n', '{\n']):
            scores["coder"] += 3
        
        # Question marks suggest simple queries
        if task.count('?') == 1 and word_count < 15:
            scores["fast"] += 2
        
        # Multiple questions or analysis requests
        if task.count('?') > 1 or any(word in task_lower for word in ['analyze', 'compare', 'evaluate']):
            scores["smart"] += 2
        
        # Get highest scoring model
        best_model = max(scores.items(), key=lambda x: x[1])
        
        # If no clear winner (all zeros or tie), use balanced
        if best_model[1] == 0:
            return "expert"  # Default for generic tasks
        
        # If tie between models, prefer in this order: fast > expert > smart > balanced > coder
        if list(scores.values()).count(best_model[1]) > 1:
            if scores["fast"] == best_model[1]:
                return "expert"
            elif scores["expert"] == best_model[1]:
                return "expert"
            elif scores["smart"] == best_model[1]:
                return "smart"
            elif scores["balanced"] == best_model[1]:
                return "balanced"
        
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
        if model == "expert":
            if any(kw in task_lower for kw in ["advanced", "complex", "expert", "professional"]):
                reasons.append("Advanced/expert level task")
            if len(task.split()) > 50:
                reasons.append("Very detailed, complex task")
            confidence = 0.95
            
        elif model == "coder":
            if any(kw in task_lower for kw in ["write code", "debug", "implement"]):
                reasons.append("Task involves coding")
            if any(pattern in task for pattern in ['```', 'def ', 'class ']):
                reasons.append("Contains code syntax")
            confidence = 0.9
            
        elif model == "smart":
            if any(kw in task_lower for kw in ["analyze", "explain deeply", "complex"]):
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
        
        print("\n" + "="*70)
        print("🧠 ROUTING DECISION")
        print("="*70)
        print(f"\nTask: {task[:100]}...")
        print(f"\nSelected Model: {result['model'].upper()}")
        print(f"Confidence: {result['confidence']*100:.0f}%")
        print(f"Reasoning: {result['reasoning']}")
        
        model_info = self.llm.MODELS[result['model']]
        print(f"\nModel Details:")
        print(f"  Name: {model_info['name']}")
        print(f"  Speed: {model_info['speed']}")
        print(f"  Quality: {model_info['quality']}")
        print("="*70 + "\n")
    
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
    print("="*70)
    
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
    
    print("\n🧪 Testing routing for different tasks:\n")
    
    for task in test_tasks:
        result = router.route_with_reasoning(task)
        print(f"Task: {task[:60]}...")
        print(f"  → Model: {result['model'].upper()} ({result['confidence']*100:.0f}% confidence)")
        print(f"  → Reason: {result['reasoning']}")
        print()
    
    print("="*70)
    print("✅ Router is smart and ready!")
