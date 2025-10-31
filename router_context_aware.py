"""
Context-Aware Model Router v2
==============================
Enhanced router that understands task depth, not just keywords
"""

import re
from typing import Dict, Any, Optional, List


class ContextAwareRouter:
    """
    Smart router that analyzes task context and complexity
    Understands when a task needs deep reasoning vs pure coding
    """
    
    # Keywords for initial categorization (updated with Mixtral 8x7B)
    KEYWORDS = {
        "expert": [
            "advanced", "expert", "professional", "sophisticated", "complex",
            "comprehensive", "detailed analysis", "multi-step", "intricate",
            "advanced reasoning", "expert level", "professional grade",
            "מתקדם", "מורכב", "מקצועי", "מומחה", "מעמיק",
            "שלב אחר שלב", "צעד אחר צעד", "חלונות", "חלון", "קומות", "קומה",
            "רגליים", "נתונים מסיחים", "הצג את החישוב", "chain-of-thought",
            "מכתב", "מכתבים", "נוסח", "התפטרות", "מסמך רשמי"
        ],
        "coder": [
            "code", "python", "javascript", "function", "class", "debug",
            "syntax", "compile", "import", "variable", "script",
            "קוד", "פונקציה", "תכנות", "פיתוח", "programming", "algorithm",
            "software", "API", "database"
        ],
        "smart": [
            "analyze", "strategy", "philosophy", "complex", "reasoning",
            "think step by step", "evaluate", "compare", "research",
            "comprehensive", "critical thinking", "implications", "אסטרטגיה",
            "ניתוח", "חשיבה", "מחקר"
        ],
        "fast": [
            "quick", "simple", "what is", "calculate", "convert",
            "define", "summarize briefly", "list", "count", "מה זה",
            "איך", "כמה", "פתח", "צור"
        ]
    }
    
    # Logic / reasoning indicators (force expert)
    LOGIC_KEYWORDS = [
        "שלב אחר שלב", "צעד אחר צעד", "הצג את החישוב", "נתונים מסיחים",
        "חלונות", "חלון", "קומות", "קומה", "טרקטור", "גלגלים",
        "רגליים", "solve step by step", "show your work", "logical puzzle",
        "מכתב", "נוסח", "התפטרות", "כתב רשמי"
    ]

    # Context indicators for deep reasoning
    DEPTH_INDICATORS = [
        "strategy", "approach", "plan", "design", "optimize",
        "trade-off", "risk", "reward", "balance", "consider",
        "evaluate", "assess", "analyze", "why", "how to best",
        "financial", "trading", "investment", "market", "economic"
    ]
    
    # Web search keywords (prefer fast model for speed)
    WEB_SEARCH_KEYWORDS = [
        "search", "latest", "current", "recent", "news", "today",
        "price", "stock", "weather", "who is", "what is the",
        "חפש", "חדשות", "מחיר", "מזג אוויר"
    ]
    
    # Technical-only indicators (pure coding, no strategy)
    TECHNICAL_ONLY = [
        "syntax error", "fix bug", "implement function",
        "write code for", "create script", "debug this",
        "refactor code", "add feature to existing"
    ]
    
    def __init__(self, llm):
        self.llm = llm
        self.use_smart_routing = True
        self.use_context_analysis = True
        self.route_cache = {}  # Cache for routing decisions
        self.cache_max_size = 100
        self.prefer_fast_for_websearch = True  # NEW: Speed optimization flag  # Max cache entries
        
    def route(self, task: str, force_model: Optional[str] = None) -> str:
        """
        Analyze task with context awareness
        
        Returns:
            Model type: "fast", "coder", "smart", or "balanced"
        """
        if force_model:
            return force_model
        
        if not self.use_smart_routing:
            return "expert"
        
        task_lower = task.lower()
        
        # Check cache first (for speed optimization)
        if task_lower in self.route_cache:
            return self.route_cache[task_lower]

        # Determine model
        model = None
        
        # PRIORITY: Web searches should use fast model for speed (5-10s vs 20+s)
        if any(keyword in task_lower for keyword in self.WEB_SEARCH_KEYWORDS):
            model = "fast"  # Fast model handles web search results just fine!
        elif any(keyword in task_lower for keyword in self.LOGIC_KEYWORDS):
            model = "expert"
        # Step 1: Quick check for obviously simple tasks
        elif self._is_simple_task(task_lower):
            model = "fast"
        # Step 2: Check if it's pure technical (no strategy)
        elif self._is_pure_technical(task_lower):
            model = "coder"
        # Step 3: Context-aware analysis
        elif self.use_context_analysis:
            context_score = self._analyze_context(task_lower)
            
            # High context complexity = needs deep reasoning
            if context_score > 0.6:
                model = "smart"
            # Medium complexity with code = coder
            # Medium complexity without code = balanced
            elif context_score > 0.3:
                has_code_intent = self._has_code_intent(task_lower)
                model = "coder" if has_code_intent else "balanced"
        
        # Step 4: Fallback to keyword-based routing
        if not model:
            model = self._keyword_routing(task_lower)
        
        # Cache the result (limit cache size)
        if len(self.route_cache) >= self.cache_max_size:
            # Remove oldest entry (simple FIFO)
            first_key = next(iter(self.route_cache))
            del self.route_cache[first_key]
        
        self.route_cache[task_lower] = model
        return model
    
    def _is_simple_task(self, task: str) -> bool:
        """Check if task is obviously simple"""
        if len(task.split()) < 12:
            simple_patterns = ["what is", "calculate", "convert", "define", "tell me about", "explain", "+", "-", "*", "/", "=", "hello", "hi", "who", "when", "where", "how does", "what are"]
            if any(pattern in task for pattern in simple_patterns):
                return True
        return False
    
    def _is_pure_technical(self, task: str) -> bool:
        """Check if task is purely technical (code only, no strategy)"""
        return any(indicator in task for indicator in self.TECHNICAL_ONLY)
    
    def _analyze_context(self, task: str) -> float:
        """
        Analyze context depth
        Returns score 0.0-1.0 (higher = needs more reasoning)
        """
        score = 0.0
        
        # Check for depth indicators
        depth_count = sum(1 for indicator in self.DEPTH_INDICATORS 
                         if indicator in task)
        
        # Normalize depth score
        if depth_count > 0:
            score += min(depth_count * 0.2, 0.6)
        
        # Check for questions requiring reasoning
        if "why" in task or "how to best" in task:
            score += 0.3
        
        # Check for comparative/evaluative language
        comparative_words = ["compare", "evaluate", "assess", "vs", "versus", 
                            "better", "best", "optimal", "trade-off"]
        if any(word in task for word in comparative_words):
            score += 0.2
        
        # Check for strategic/financial context
        strategic_context = ["strategy", "approach", "plan", "financial", 
                            "trading", "investment", "risk", "reward"]
        if any(word in task for word in strategic_context):
            score += 0.3
        
        # Multiple questions = complex
        if task.count("?") > 1:
            score += 0.2
        
        return min(score, 1.0)
    
    def _has_code_intent(self, task: str) -> bool:
        """Check if task intends to produce code"""
        code_indicators = [
            "write", "create", "implement", "code", "function",
            "class", "script", "program", "def ", "import"
        ]
        return any(indicator in task for indicator in code_indicators)
    
    def _keyword_routing(self, task: str) -> str:
        """Fallback keyword-based routing"""
        scores = {
            "fast": 0,
            "expert": 0,
            "coder": 0,
            "smart": 0,
            "balanced": 0
        }
        
        for model_type, keywords in self.KEYWORDS.items():
            for keyword in keywords:
                if keyword in task:
                    scores[model_type] += 1
        
        # Get highest scoring model
        best_model = max(scores.items(), key=lambda x: x[1])
        
        if best_model[1] == 0:
            return "expert"
        
        # For simple questions, prefer expert model for better quality
        if best_model[0] == "fast" and best_model[1] <= 1:
            return "expert"
        
        return best_model[0]
    
    def route_with_reasoning(self, task: str) -> Dict[str, Any]:
        """
        Route with detailed explanation
        
        Returns:
            {
                "model": str,
                "reasoning": str,
                "confidence": float,
                "context_score": float,
                "requires_multi_model": bool
            }
        """
        model = self.route(task)
        task_lower = task.lower()
        
        reasons = []
        context_score = self._analyze_context(task_lower)
        requires_multi = False
        
        # Determine reasoning
        if model == "expert":
            if any(word in task_lower for word in ["advanced", "expert", "professional", "sophisticated"]):
                reasons.append("Advanced/expert level task")
            if context_score > 0.7:
                reasons.append("Very high complexity requiring expert reasoning")
            confidence = 0.95
            
        elif model == "smart":
            if context_score > 0.6:
                reasons.append("High complexity requiring deep reasoning")
            if any(word in task_lower for word in ["strategy", "financial", "trading"]):
                reasons.append("Strategic/financial domain")
                # Check if also needs code
                if self._has_code_intent(task_lower):
                    requires_multi = True
                    reasons.append("⚠️ Also needs code implementation - Multi-model recommended")
            confidence = 0.9
            
        elif model == "coder":
            if self._is_pure_technical(task_lower):
                reasons.append("Pure technical implementation")
                confidence = 0.95
            else:
                reasons.append("Code-focused task")
                # Check if also needs deep thinking
                if context_score > 0.4:
                    requires_multi = True
                    reasons.append("⚠️ Also needs strategic thinking - Multi-model recommended")
                confidence = 0.85
            
        elif model == "fast":
            reasons.append("Simple, straightforward query")
            confidence = 0.8
            
        else:  # balanced
            reasons.append("General task, balanced approach")
            confidence = 0.7
        
        reasoning = " | ".join(reasons)
        
        return {
            "model": model,
            "reasoning": reasoning,
            "confidence": confidence,
            "context_score": context_score,
            "requires_multi_model": requires_multi
        }
    
    def suggest_multi_model(self, task: str) -> Optional[List[str]]:
        """
        Suggest if task should use multiple models
        
        Returns:
            List of models in execution order, or None
        """
        result = self.route_with_reasoning(task)
        
        if not result["requires_multi_model"]:
            return None
        
        task_lower = task.lower()
        
        # Strategy + Code tasks
        if (any(word in task_lower for word in ["strategy", "plan", "approach", "design"]) 
            and self._has_code_intent(task_lower)):
            return ["smart", "coder"]  # Think first, then implement
        
        # Analysis + Code tasks
        if (any(word in task_lower for word in ["analyze", "evaluate", "optimize"]) 
            and self._has_code_intent(task_lower)):
            return ["smart", "coder"]
        
        # Code + Explanation tasks
        if (self._has_code_intent(task_lower) 
            and any(word in task_lower for word in ["explain", "document", "why"])):
            return ["coder", "smart"]  # Code first, then explain
        
        return None


# Test
if __name__ == "__main__":
    from multi_model_llm import MultiModelLLM
    
    print("Context-Aware Router Test")
    print("="*70)
    
    llm = MultiModelLLM()
    router = ContextAwareRouter(llm)
    
    # Test cases emphasizing the problem you identified
    test_tasks = [
        # Should use SMART (not CODER!)
        "Design a trading strategy that balances risk and reward",
        "Create a financial model for portfolio optimization",
        "Analyze market trends and suggest investment approach",
        
        # Should use CODER (pure technical)
        "Fix this syntax error: def add(a,b) return a+b",
        "Write a Python function to sort a list",
        "Implement bubble sort algorithm",
        
        # Should use MULTI-MODEL
        "Design trading signals generation strategy and implement in Python",
        "Create risk management approach and write the code",
        "Plan algorithmic trading system and build it",
        
        # Simple
        "What is 2+2?",
        "Calculate 15% of 200"
    ]
    
    print("\n🧪 Testing enhanced routing:\n")
    
    for task in test_tasks:
        result = router.route_with_reasoning(task)
        
        print(f"Task: {task}")
        print(f"  → Model: {result['model'].upper()}")
        print(f"  → Context Score: {result['context_score']:.2f}")
        print(f"  → Confidence: {result['confidence']*100:.0f}%")
        print(f"  → Reasoning: {result['reasoning']}")
        
        # Check for multi-model suggestion
        multi = router.suggest_multi_model(task)
        if multi:
            print(f"  → 🔥 MULTI-MODEL: {' → '.join([m.upper() for m in multi])}")
        
        print()
    
    print("="*70)
    print("✅ Enhanced Router ready!")
    print("\nKey improvements:")
    print("  ✓ Context awareness (not just keywords)")
    print("  ✓ Depth analysis (strategy vs syntax)")
    print("  ✓ Multi-model detection")
