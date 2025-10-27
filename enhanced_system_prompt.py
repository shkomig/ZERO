"""
Enhanced System Prompts for Zero Agent
=======================================
Simple, clean prompts for clear responses
"""

# System Prompt for CLEAN, SIMPLE responses
DETAILED_SYSTEM_PROMPT = """You are Zero Agent, an AI assistant. Answer in Hebrew clearly and concisely.

Rules:
1. Short, direct answers for simple questions
2. Detailed answers for complex questions  
3. No unnecessary introductions
4. No emojis or symbols
5. Clean formatting

Examples:
Q: 5+5
A: 10

Q: כמה זה 6+5
A: 11

Q: מה זה Python?
A: Python היא שפת תכנות רב-תכליתית, קלה ללמידה ושימושית לפיתוח אפליקציות, ניתוח נתונים ואוטומציה."""

# Concise system prompt for short answers
CONCISE_SYSTEM_PROMPT = """You are Zero, an AI assistant. Give brief, direct answers in Hebrew.

Examples:
Q: 5+5  
A: 10

Q: מה זה Python?
A: שפת תכנות רב-תכליתית"""


def get_system_prompt(detailed: bool = True) -> str:
    """
    Get appropriate system prompt
    
    Args:
        detailed: Use detailed mode (True) or concise (False)
        
    Returns:
        System prompt string
    """
    return DETAILED_SYSTEM_PROMPT if detailed else CONCISE_SYSTEM_PROMPT


def build_enhanced_prompt(
    user_message: str,
    context: str = "",
    search_results: str = "",
    action_result: str = "",
    detailed: bool = True
) -> str:
    """
    Build a complete prompt with all components
    
    Args:
        user_message: User's question
        context: Conversation history
        search_results: Results from web search
        action_result: Result of action (if any)
        detailed: Use detailed mode
        
    Returns:
        Complete prompt string
    """
    prompt = get_system_prompt(detailed) + "\n\n"
    
    # 1. Context (if available)
    if context:
        prompt += f"## הקשר מהשיחה הקודמת:\n{context}\n\n"
    
    # 2. Search results (if available)
    if search_results:
        prompt += f"## מידע נוסף מהרשת:\n{search_results}\n\n"
    
    # 3. Action result (if available)
    if action_result:
        prompt += f"## פעולה שבוצעה:\n{action_result}\n\n"
    
    # 4. User message
    prompt += f"ש: {user_message}\nת: "
    
    return prompt


# Test
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("Enhanced System Prompt Test")
    print("="*60)
    
    # Test detailed mode
    print("\n[1] Detailed Mode Prompt:")
    print("-"*60)
    prompt = build_enhanced_prompt(
        user_message="5+5",
        detailed=True
    )
    print(prompt)
    
    # Test concise mode
    print("\n[2] Concise Mode Prompt:")
    print("-"*60)
    prompt = build_enhanced_prompt(
        user_message="5+5",
        detailed=False
    )
    print(prompt)
    
    print("\n" + "="*60)
    print("[OK] Enhanced System Prompts ready!")
