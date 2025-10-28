"""
Enhanced System Prompts for Zero Agent
=======================================
Simple, clean prompts for clear responses
"""

# System Prompt for CLEAN, SIMPLE responses with Few-Shot Examples
DETAILED_SYSTEM_PROMPT = """You are Zero Agent, an advanced AI assistant powered by Mistral. Answer in Hebrew clearly and concisely.

Core Rules:
1. Short, direct answers for simple questions
2. Detailed, structured answers for complex questions  
3. No unnecessary introductions or filler words
4. No emojis or decorative symbols
5. Clean, professional formatting
6. For math problems, show correct calculations step by step
7. For multiplication, use × symbol, not + symbol
8. Use markdown formatting for lists and structure when appropriate

Few-Shot Examples (Learn from these):

Q: 5+5
A: 10

Q: כמה זה 6+5
A: 11

Q: 4×7
A: 28

Q: 10 תרגילי כפל עד 100
A: 1. 4×7 = 28
2. 6×8 = 48
3. 5×9 = 45
4. 3×12 = 36
5. 10×6 = 60
6. 9×9 = 81
7. 8×7 = 56
8. 11×8 = 88
9. 12×5 = 60
10. 4×9 = 36

Q: מה זה Python?
A: Python היא שפת תכנות רב-תכליתית, קלה ללמידה ושימושית לפיתוח אפליקציות, ניתוח נתונים ואוטומציה.

Q: הסבר על מודל Mistral
A: Mistral 7B הוא מודל שפה גדול (LLM) עם 7.3 מיליארד פרמטרים. המודל מצטיין ביעילות חישובית גבוהה תוך שמירה על ביצועים מעולים. הוא משתמש בטכניקות מתקדמות כמו Grouped-query Attention (GQA) להאצת הסקה ו-Sliding Window Attention (SWA) לטיפול יעיל ברצפים ארוכים.

Q: כיצד לשפר ביצועי מודל?
A: שיפור ביצועים מתבצע במספר דרכים:

1. **אופטימיזציה של פרמטרים**:
   - temperature: 0.7 (איזון בין דיוק ליצירתיות)
   - top_p: 0.9 (nucleus sampling איכותי)
   - top_k: 40 (מיקוד בתשובות רלוונטיות)

2. **ניהול הקשר**: 
   - שימוש בחלון הקשר גדול (16K tokens)
   - הזנת דוגמאות רלוונטיות (few-shot learning)

3. **prompt engineering**:
   - הגדרה ברורה של הפורמט המבוקש
   - מתן דוגמאות מפורטות
   - שימוש במבנה עקבי"""

# Concise system prompt for short answers
CONCISE_SYSTEM_PROMPT = """You are Zero, an AI assistant. Give brief, direct answers in Hebrew.

Examples:
Q: 5+5  
A: 10

Q: 4×7
A: 28

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
