#!/usr/bin/env python3
"""
Test the router to see which model it selects
"""

import sys
sys.path.append('.')

from router_context_aware import ContextAwareRouter

# Test the router
router = ContextAwareRouter(llm=None)

# Test Hebrew question
hebrew_question = "שלום, איך אתה היום?"
result = router.route_with_reasoning(hebrew_question)
print(f"Hebrew question: {hebrew_question}")
print(f"Selected model: {result['model']}")
print(f"Reasoning: {result['reasoning']}")

# Debug: Check what keywords are found
print(f"\nDebug - Checking keywords in Hebrew question:")
for model_type, keywords in router.KEYWORDS.items():
    found_keywords = [kw for kw in keywords if kw in hebrew_question.lower()]
    if found_keywords:
        print(f"  {model_type}: {found_keywords}")

# Test English question
english_question = "Hello, how are you today?"
result = router.route_with_reasoning(english_question)
print(f"\nEnglish question: {english_question}")
print(f"Selected model: {result['model']}")
print(f"Reasoning: {result['reasoning']}")
