"""
Test Router Logic - Debug with NEW SMART LOGIC
"""

# Test different messages
test_messages = [
    ("תבנה לי אפליקציית Flask", "coder"),
    ("כתוב לי קוד Python", "coder"),
    ("צור אפליקציה עם מבנה מלא", "coder"),
    ("מה זה API?", "hebrew"),
    ("הסבר לי על Docker", "hebrew"),
    ("5+5", "hebrew"),
    ("תבנה API ב-Flask", "coder"),
    ("ספר לי על Python", "hebrew"),
]

# Simulate NEW router logic
for message, expected in test_messages:
    message_lower = message.lower()
    
    scores = {"hebrew": 0, "coder": 0, "smart": 0}
    
    # STEP 1: Explanation triggers
    explanation_triggers = ["מה זה", "מהו", "מהי", "הסבר", "ספר לי"]
    is_explanation = any(trigger in message_lower for trigger in explanation_triggers)
    if is_explanation:
        scores["hebrew"] += 5
    
    # STEP 2: Code generation
    code_action_words = ["תבנה", "צור", "כתוב", "בנה", "פתח", "קוד"]
    is_code_generation = any(action in message_lower for action in code_action_words)
    # Extra boost if "קוד" appears
    if "קוד" in message_lower or "code" in message_lower:
        scores["coder"] += 3
    if is_code_generation:
        scores["coder"] += 5
    
    # STEP 3: Hebrew baseline
    has_hebrew = any('\u0590' <= char <= '\u05FF' for char in message)
    if has_hebrew and not is_code_generation:
        scores["hebrew"] += 1
    
    # STEP 4: Short math/simple questions -> hebrew (fast)
    if len(message) < 15 and any(char in message for char in "0123456789+-*/="):
        scores["hebrew"] += 2
    
    # Decide
    model = max(scores, key=scores.get)
    if all(v == 0 for v in scores.values()):
        model = "hebrew" if has_hebrew else "smart"
    
    status = "[OK]" if model == expected else "[FAIL]"
    print(f"{status} '{message}' -> {model} (expected: {expected}) | Scores: {scores}")

