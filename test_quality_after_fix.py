"""
בדיקת איכות תשובות Zero Agent לאחר תיקון
================================================
בודק את השאלה שגרמה לבעיה + שאלות נוספות
"""

import requests
import json
import time
import sys

# Fix encoding for Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

API_URL = "http://localhost:8080/api/chat"

# צבעים לטרמינל
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def test_question(question: str, expected_keywords: list, avoid_keywords: list):
    """
    בודק שאלה אחת
    
    Args:
        question: השאלה לבדיקה
        expected_keywords: מילות מפתח שצריכות להופיע
        avoid_keywords: מילות מפתח שאסור שיופיעו
    """
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}🔍 שאלה: {question}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    try:
        start_time = time.time()
        response = requests.post(
            API_URL,
            json={"message": question, "use_memory": False},
            timeout=60
        )
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get('response', '')
            model = data.get('model_used', '')
            
            print(f"{YELLOW}📝 תשובה שהתקבלה:{RESET}")
            print(f"{answer}\n")
            print(f"{BLUE}⏱️  זמן תגובה: {elapsed:.2f} שניות{RESET}")
            print(f"{BLUE}🤖 מודל: {model}{RESET}\n")
            
            # בדיקות איכות
            passed_tests = []
            failed_tests = []
            
            # 1. בדיקת מילות מפתח נדרשות
            for keyword in expected_keywords:
                if keyword in answer:
                    passed_tests.append(f"✓ נמצא: '{keyword}'")
                else:
                    failed_tests.append(f"✗ חסר: '{keyword}'")
            
            # 2. בדיקת מילות מפתח אסורות
            for keyword in avoid_keywords:
                if keyword not in answer:
                    passed_tests.append(f"✓ לא נמצא (טוב): '{keyword}'")
                else:
                    failed_tests.append(f"✗ נמצא (רע): '{keyword}'")
            
            # 3. בדיקות נוספות
            if not answer.startswith("ברוכים") and not answer.startswith("אציג"):
                passed_tests.append("✓ התחלה נכונה (ללא פתיחות מיותרות)")
            else:
                failed_tests.append("✗ יש פתיחה מיותרת")
            
            if len(answer) > 50:  # תשובה לא ריקה
                passed_tests.append("✓ תשובה מספיק ארוכה")
            else:
                failed_tests.append("✗ תשובה קצרה מדי")
            
            # הצגת תוצאות
            print(f"{GREEN}✅ בדיקות שעברו:{RESET}")
            for test in passed_tests:
                print(f"  {test}")
            
            if failed_tests:
                print(f"\n{RED}❌ בדיקות שנכשלו:{RESET}")
                for test in failed_tests:
                    print(f"  {test}")
                return False
            else:
                print(f"\n{GREEN}{'='*70}")
                print(f"🎉 כל הבדיקות עברו בהצלחה!")
                print(f"{'='*70}{RESET}\n")
                return True
        else:
            print(f"{RED}❌ שגיאה: {response.status_code}{RESET}")
            print(f"תשובה: {response.text}")
            return False
            
    except Exception as e:
        print(f"{RED}❌ חריגה: {str(e)}{RESET}")
        return False


def main():
    """
    מריץ את כל הבדיקות
    """
    print(f"""
{BLUE}{'='*70}
🧪 בדיקת איכות Zero Agent - לאחר תיקון
{'='*70}{RESET}

מריץ בדיקות על שאלות שגרמו לבעיות בעבר...
    """)
    
    tests = [
        {
            "question": "הצג את שני הטיעונים המרכזיים בעד ונגד רגולציה ממשלתית הדוקה של רשתות חברתיות גדולות. השתמש בשפה עברית רשמית וניטרלית, תוך הקפדה על הפרדה ברורה בין הטיעונים.",
            "expected": ["טיעונים בעד", "טיעונים נגד", "1.", "2."],
            "avoid": ["ברוכים", "אציג", "הפסדים", "מגברת", "טפשית בניסי"]
        },
        {
            "question": "מה ההבדל בין Latency ל-Throughput?",
            "expected": ["זמן אחזור", "תפוקה"],
            "avoid": ["Latency", "Throughput", "ברוכים"]
        },
        {
            "question": "בחדר יש 5 חתולים. לכל חתול יש 4 רגליים. כמה רגליים של בני אדם נמצאות בחדר, בהנחה שיש בחדר רק את מי שצריך כדי לספור את החתולים?",
            "expected": ["2", "אדם אחד", "רגליים"],
            "avoid": ["20", "24", "ברוכים"]
        },
        {
            "question": "כמה זה 15 × 23?",
            "expected": ["345"],
            "avoid": ["ברוכים", "אציג", "אסביר"]
        }
    ]
    
    results = []
    for i, test in enumerate(tests, 1):
        print(f"\n{YELLOW}📌 בדיקה {i}/{len(tests)}{RESET}")
        passed = test_question(
            test["question"],
            test["expected"],
            test["avoid"]
        )
        results.append(passed)
        time.sleep(2)  # המתנה קצרה בין בדיקות
    
    # סיכום
    print(f"\n{BLUE}{'='*70}")
    print(f"📊 סיכום תוצאות")
    print(f"{'='*70}{RESET}\n")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"✅ עברו: {passed}/{total}")
    print(f"❌ נכשלו: {total - passed}/{total}")
    print(f"📈 אחוז הצלחה: {percentage:.1f}%\n")
    
    if percentage >= 75:
        print(f"{GREEN}🎉 הצלחה! המערכת עובדת טוב{RESET}")
    elif percentage >= 50:
        print(f"{YELLOW}⚠️  ישנם עוד שיפורים לבצע{RESET}")
    else:
        print(f"{RED}❌ דרושים תיקונים נוספים{RESET}")


if __name__ == "__main__":
    print(f"\n{YELLOW}ודא שהשרת רץ על http://localhost:8080{RESET}\n")
    input("לחץ Enter כדי להתחיל...")
    main()

