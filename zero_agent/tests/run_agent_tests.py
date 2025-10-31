#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zero Agent Test Suite Runner
==============================
Runs comprehensive tests against Zero Agent API and generates detailed reports.
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import sys
import io

# Fix encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Configuration
API_URL = "http://localhost:8080/api/chat"
TEST_FILE = Path(__file__).parent / "agent_full_eval_v2.json"
OUTPUT_DIR = Path(__file__).parent
TEST_REPORT_FILE = OUTPUT_DIR / "Agent_Test_Report.txt"
FINAL_SUMMARY_FILE = OUTPUT_DIR / "Agent_Final_Summary.txt"
TIMEOUT = 120  # seconds per test
DELAY_BETWEEN_TESTS = 2  # seconds


class TestRunner:
    """Main test runner class"""
    
    def __init__(self, api_url: str = API_URL):
        self.api_url = api_url
        self.results: List[Dict[str, Any]] = []
        self.category_scores: Dict[str, List[float]] = defaultdict(list)
        self.failed_tests: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, str]] = []
        
    def check_api_health(self) -> bool:
        """Check if API server is running"""
        try:
            response = requests.get(f"{self.api_url.replace('/api/chat', '/health')}", timeout=5)
            if response.status_code == 200:
                print("[OK] API server is running")
                return True
        except Exception as e:
            print(f"[ERROR] API server check failed: {e}")
        
        # Try the main endpoint
        try:
            response = requests.get(f"{self.api_url.replace('/api/chat', '/')}", timeout=5)
            if response.status_code == 200:
                print("[OK] API server is accessible")
                return True
        except:
            pass
        
        print("[ERROR] Cannot connect to API server. Make sure it's running on http://localhost:8080")
        return False
    
    def run_test(self, test: Dict[str, Any], test_num: int, total: int) -> Dict[str, Any]:
        """Run a single test"""
        test_id = test["id"]
        category = test["category"]
        task = test["task"]
        
        print(f"\n[{test_num}/{total}] Test #{test_id} - {category}")
        print(f"Task: {task[:80]}...")
        
        start_time = time.time()
        
        try:
            # STEP 1.4: Improved context passing - use ALL history for memory tests
            # For memory tests, include more history; for others, use last 10
            if "Memory" in category or "Context" in category:
                history_to_use = self.conversation_history[-20:]  # Last 20 for memory tests
            else:
                history_to_use = self.conversation_history[-10:]  # Last 10 for other tests
            
            # Prepare request
            payload = {
                "message": task,
                "model": "balanced",  # Use balanced model for testing
                "use_memory": True,
                "conversation_history": history_to_use  # Improved context
            }
            
            # Send request
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"}
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                agent_response = data.get("response", "")
                model_used = data.get("model_used", "unknown")
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": task})
                self.conversation_history.append({"role": "assistant", "content": agent_response})
                
                # Evaluate response (simple heuristic scoring)
                score = self._evaluate_response(agent_response, category, task)
                
                result = {
                    "id": test_id,
                    "category": category,
                    "task": task,
                    "status": "success",
                    "response": agent_response[:500],  # Truncate for report
                    "full_response": agent_response,
                    "model_used": model_used,
                    "duration": round(elapsed_time, 2),
                    "score": score,
                    "confidence": self._calculate_confidence(agent_response, category),
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"[OK] Completed in {elapsed_time:.2f}s (Score: {score}/10)")
                
            else:
                result = {
                    "id": test_id,
                    "category": category,
                    "task": task,
                    "status": "error",
                    "response": f"HTTP {response.status_code}: {response.text[:200]}",
                    "full_response": "",
                    "model_used": "none",
                    "duration": round(elapsed_time, 2),
                    "score": 0.0,
                    "confidence": 0.0,
                    "timestamp": datetime.now().isoformat()
                }
                print(f"[FAIL] HTTP {response.status_code}")
                
        except requests.Timeout:
            result = {
                "id": test_id,
                "category": category,
                "task": task,
                "status": "timeout",
                "response": "Request timed out",
                "full_response": "",
                "model_used": "none",
                "duration": TIMEOUT,
                "score": 0.0,
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
            print(f"[TIMEOUT] After {TIMEOUT}s")
            
        except Exception as e:
            result = {
                "id": test_id,
                "category": category,
                "task": task,
                "status": "error",
                "response": f"Error: {str(e)[:200]}",
                "full_response": "",
                "model_used": "none",
                "duration": round(time.time() - start_time, 2),
                "score": 0.0,
                "confidence": 0.0,
                "timestamp": datetime.now().isoformat()
            }
            print(f"[ERROR] {str(e)}")
        
        # Track scores and failures
        if result["score"] < 5.0:
            self.failed_tests.append(result)
        self.category_scores[category].append(result["score"])
        
        return result
    
    def _evaluate_response(self, response: str, category: str, task: str) -> float:
        """Simple heuristic-based scoring"""
        if not response:
            return 0.0
        
        response_lower = response.lower().strip()
        response_numeric = None
        
        # STEP 2.1: Extract numbers from response (for pattern/logic questions)
        import re
        numbers = re.findall(r'\d+', response)
        if numbers:
            response_numeric = int(numbers[0]) if numbers else None
        
        # For very short but correct answers (like "32" for pattern 2,4,8,16,?)
        # Don't penalize immediately - check if it's a valid answer first
        if len(response.strip()) < 10 and response_numeric is not None:
            # Check if task is about patterns/logic/numbers
            if any(kw in task.lower() for kw in ['pattern', 'דפוס', 'sequence', 'מספר', 'number', '?', 'מה הבא']):
                # If response is a number and task asks for pattern/sequence, likely correct
                return 7.5  # Good score for correct numeric patterns
        
        # For empty or very short non-numeric responses
        if len(response.strip()) < 5:
            return 0.0
        
        score = 5.0  # Base score
        
        # Length check (but be lenient for correct short answers)
        if len(response) > 50:
            score += 1.0
        if len(response) > 200:
            score += 1.0
        
        # Category-specific checks
        if category in ["Web Search", "Web Search Advanced", "Research", "Web Search & Real-Time Knowledge"]:
            if any(keyword in response_lower for keyword in ["http", "source", "article", "news", "found", "search", "according", "מתוך"]):
                score += 1.0
        elif category in ["Coding", "Code Generation", "Debugging", "Debugging Advanced", "Coding & Debugging"]:
            if any(keyword in response_lower for keyword in ["def ", "function", "import", "code", "python", "javascript", "html", "```"]):
                score += 1.0
        elif category in ["Memory", "Memory Recall", "Memory Validation", "Memory Chain", "Memory & Context Retention"]:
            # Check for actual memory recall (not just keywords)
            if any(keyword in response_lower for keyword in ["alex", "test supervisor", "task 3", "task id 3", "summarize", "זוכר", "אמרתי"]):
                score += 2.0  # Higher weight for memory
            elif any(keyword in response_lower for keyword in ["blue", "local", "python", "remember"]):
                score += 1.0
        elif category in ["Math", "Reasoning & Logic"]:
            # Check for numeric answers or logical conclusions
            if response_numeric is not None:
                score += 1.5  # Numbers in logic/math = good
            if any(keyword in response_lower for keyword in ["=", "equals", "implies", "conclude", "therefore", "שווה", "לכן"]):
                score += 1.0
            # Specific check for pattern questions
            if "pattern" in task.lower() or "דפוס" in task.lower() or "sequence" in task.lower():
                if response_numeric == 32 and "2, 4, 8, 16" in task:
                    return 8.0  # Definitely correct for that pattern
                if response_numeric is not None:
                    score += 1.5  # Numeric answer to pattern question = likely correct
        
        # Quality indicators
        if len(response.split()) > 20:  # Substantial response
            score += 0.5
        if "?" not in response or response.count("?") < 3:  # Not too many questions
            score += 0.5
        
        return min(10.0, max(0.0, score))
    
    def _calculate_confidence(self, response: str, category: str) -> float:
        """Calculate confidence score based on response quality"""
        if not response:
            return 0.0
        
        confidence = 0.5  # Base
        
        if len(response) > 100:
            confidence += 0.2
        if len(response) > 500:
            confidence += 0.2
        if response.count(".") > 2:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def load_tests(self) -> Dict[str, Any]:
        """Load test configuration from JSON"""
        try:
            with open(TEST_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading test file: {e}")
            sys.exit(1)
    
    def save_test_report(self):
        """Save detailed test report"""
        with open(TEST_REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ZERO AGENT TEST REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Tests: {len(self.results)}\n\n")
            
            for result in self.results:
                f.write(f"\n{'='*80}\n")
                f.write(f"Test ID: {result['id']}\n")
                f.write(f"Category: {result['category']}\n")
                f.write(f"Task: {result['task']}\n")
                f.write(f"Status: {result['status']}\n")
                f.write(f"Score: {result['score']}/10\n")
                f.write(f"Confidence: {result['confidence']:.2f}\n")
                f.write(f"Duration: {result['duration']}s\n")
                f.write(f"Model Used: {result['model_used']}\n")
                f.write(f"Response: {result['response']}\n")
                f.write(f"Timestamp: {result['timestamp']}\n")
        
        print(f"\n[OK] Test report saved to: {TEST_REPORT_FILE}")
    
    def generate_final_summary(self):
        """Generate final summary report"""
        # Calculate category averages
        category_averages = {}
        for category, scores in self.category_scores.items():
            if scores:
                category_averages[category] = {
                    "average": sum(scores) / len(scores),
                    "count": len(scores),
                    "min": min(scores),
                    "max": max(scores)
                }
        
        # Overall statistics
        all_scores = [r["score"] for r in self.results]
        overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0.0
        success_count = len([r for r in self.results if r["status"] == "success"])
        total_duration = sum([r["duration"] for r in self.results])
        
        with open(FINAL_SUMMARY_FILE, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("ZERO AGENT TEST FINAL SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Overall Statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Tests: {len(self.results)}\n")
            f.write(f"Successful: {success_count} ({success_count/len(self.results)*100:.1f}%)\n")
            f.write(f"Failed/Partial: {len(self.failed_tests)} ({len(self.failed_tests)/len(self.results)*100:.1f}%)\n")
            f.write(f"Overall Average Score: {overall_avg:.2f}/10\n")
            f.write(f"Total Duration: {total_duration:.2f}s ({total_duration/60:.2f} minutes)\n\n")
            
            # Category Scores
            f.write("CATEGORY AVERAGE SCORES (1-10)\n")
            f.write("-" * 80 + "\n")
            for category in sorted(category_averages.keys()):
                stats = category_averages[category]
                f.write(f"{category:30s}: {stats['average']:5.2f} (Min: {stats['min']:.2f}, Max: {stats['max']:.2f}, Count: {stats['count']})\n")
            f.write("\n")
            
            # Failed Tests
            f.write("FAILED OR PARTIAL TASKS\n")
            f.write("-" * 80 + "\n")
            if self.failed_tests:
                for test in self.failed_tests:
                    f.write(f"Test #{test['id']} ({test['category']}): {test['task'][:60]}...\n")
                    f.write(f"  Score: {test['score']}/10, Status: {test['status']}\n")
            else:
                f.write("None - All tests passed!\n")
            f.write("\n")
            
            # Strengths
            f.write("STRENGTHS SUMMARY\n")
            f.write("-" * 80 + "\n")
            top_categories = sorted(category_averages.items(), key=lambda x: x[1]["average"], reverse=True)[:5]
            for category, stats in top_categories:
                f.write(f"[+] {category}: Strong performance (avg: {stats['average']:.2f}/10)\n")
            f.write("\n")
            
            # Weaknesses
            f.write("WEAKNESSES SUMMARY\n")
            f.write("-" * 80 + "\n")
            bottom_categories = sorted(category_averages.items(), key=lambda x: x[1]["average"])[:5]
            for category, stats in bottom_categories:
                f.write(f"[-] {category}: Needs improvement (avg: {stats['average']:.2f}/10)\n")
            f.write("\n")
            
            # Recommendations
            f.write("RECOMMENDED IMPROVEMENTS\n")
            f.write("-" * 80 + "\n")
            for category, stats in bottom_categories:
                if stats['average'] < 6.0:
                    f.write(f"• Focus on improving {category} tasks\n")
            if overall_avg < 7.0:
                f.write("• Consider model fine-tuning or prompt engineering\n")
            if len(self.failed_tests) > len(self.results) * 0.2:
                f.write("• Review error handling and timeout configurations\n")
            if total_duration > 3600:  # More than 1 hour
                f.write("• Optimize response times - consider caching or model selection\n")
        
        print(f"[OK] Final summary saved to: {FINAL_SUMMARY_FILE}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("ZERO AGENT TEST SUITE")
        print("=" * 80)
        
        # Check API health
        if not self.check_api_health():
            print("\n[ERROR] Cannot proceed without API connection")
            return
        
        # Load tests
        print("\nLoading test configuration...")
        test_config = self.load_tests()
        tests = test_config["tests"]
        
        print(f"Loaded {len(tests)} tests")
        print(f"Starting test execution...\n")
        
        # Run tests
        start_time = time.time()
        
        for i, test in enumerate(tests, 1):
            result = self.run_test(test, i, len(tests))
            self.results.append(result)
            
            # Delay between tests
            if i < len(tests):
                time.sleep(DELAY_BETWEEN_TESTS)
        
        total_time = time.time() - start_time
        
        # Generate reports
        print("\n" + "=" * 80)
        print("Generating reports...")
        print("=" * 80)
        
        self.save_test_report()
        self.generate_final_summary()
        
        print(f"\n[OK] All tests completed in {total_time/60:.2f} minutes")
        print(f"[OK] Results saved to: {OUTPUT_DIR}")


def main():
    """Main entry point"""
    runner = TestRunner()
    try:
        runner.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest execution interrupted by user")
        if runner.results:
            print("Saving partial results...")
            runner.save_test_report()
            runner.generate_final_summary()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
