#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Speed Improvement - Before vs After
"""
import requests
import time
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Test queries that should now be FAST
test_queries = [
    "search for latest AI news",
    "what is the current price of NVDA?",
    "latest news about SpaceX",
    "who is Elon Musk?",
    "current weather in New York"
]

print("="*70)
print("  SPEED TEST - Web Search Optimization")
print("="*70)
print("\nTesting queries that should now use FAST model...")
print("Target: < 10 seconds per query\n")

total_time = 0
passed = 0
failed = 0

for i, query in enumerate(test_queries, 1):
    print(f"\n[{i}/{len(test_queries)}] {query}")
    print("-"*70)
    
    start = time.time()
    
    try:
        response = requests.post(
            "http://localhost:8080/api/chat",
            json={"message": query, "use_memory": False},
            timeout=30
        )
        
        duration = time.time() - start
        total_time += duration
        
        if response.status_code == 200:
            data = response.json()
            model = data.get('model_used', 'unknown')
            
            print(f"Model Used: {model}")
            print(f"Duration: {duration:.2f}s")
            
            # Check if using fast model and under 10s
            if model == "fast" and duration < 10:
                print(f"Status: [PASS] Fast model + Quick response!")
                passed += 1
            elif model == "fast":
                print(f"Status: [SLOW] Fast model but took {duration:.2f}s")
                passed += 1
            elif duration < 10:
                print(f"Status: [PASS] Quick response even with {model}")
                passed += 1
            else:
                print(f"Status: [FAIL] Using {model} model - took {duration:.2f}s")
                failed += 1
        else:
            print(f"Status: [ERROR] HTTP {response.status_code}")
            failed += 1
            
    except Exception as e:
        duration = time.time() - start
        print(f"Status: [ERROR] {e}")
        failed += 1

# Summary
print("\n" + "="*70)
print("  RESULTS")
print("="*70)
print(f"\nTotal Tests: {len(test_queries)}")
print(f"Passed: {passed}")
print(f"Failed: {failed}")
print(f"\nAverage Time: {total_time/len(test_queries):.2f}s")
print(f"Total Time: {total_time:.2f}s")

if passed == len(test_queries) and total_time/len(test_queries) < 10:
    print("\n[SUCCESS] Speed optimization is WORKING!")
    print("Web searches are now FAST!")
elif passed >= len(test_queries) * 0.8:
    print("\n[GOOD] Most queries are fast now!")
else:
    print("\n[NEEDS IMPROVEMENT] Some queries still slow")
    print("\nTroubleshooting:")
    print("  1. Restart API server: python api_server.py")
    print("  2. Check if router changes loaded")

print("="*70)

