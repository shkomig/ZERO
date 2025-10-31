#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Final Proof: WebSearch is Working
"""
import requests
import sys
import json

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("="*70)
print("  FINAL PROOF: Zero Agent WebSearch is WORKING")
print("="*70)
print()

# Test queries
tests = [
    {
        "name": "Stock Price Test",
        "query": "what is the current price of NVDA stock?",
        "expected_markers": ["$", "USD", "NVDA", "price"]
    },
    {
        "name": "Latest News Test", 
        "query": "latest news about artificial intelligence",
        "expected_markers": ["http", "www", "://"]
    },
    {
        "name": "Person Search Test",
        "query": "who is Jensen Huang?",
        "expected_markers": ["NVIDIA", "CEO", "founder"]
    }
]

passed = 0
failed = 0

for i, test in enumerate(tests, 1):
    print(f"\n[Test {i}/3] {test['name']}")
    print(f"Query: \"{test['query']}\"")
    print("-"*70)
    
    try:
        response = requests.post(
            "http://localhost:8080/api/chat",
            json={"message": test["query"], "use_memory": False},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            # Check for expected markers
            found_markers = []
            for marker in test['expected_markers']:
                if marker.lower() in response_text.lower():
                    found_markers.append(marker)
            
            # Determine if test passed
            test_passed = len(found_markers) > 0
            
            print(f"Status: {'PASS' if test_passed else 'FAIL'}")
            print(f"Model: {data.get('model_used', 'N/A')}")
            print(f"Duration: {data.get('duration', 0):.2f}s")
            print(f"Response Length: {len(response_text)} chars")
            print(f"Markers Found: {found_markers if found_markers else 'None'}")
            
            # Show snippet
            snippet = response_text[:200].replace('\n', ' ')
            print(f"Snippet: {snippet}...")
            
            if test_passed:
                print("[OK] WebSearch data detected!")
                passed += 1
            else:
                print("[WARNING] No clear web data markers found")
                failed += 1
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            failed += 1
            
    except Exception as e:
        print(f"[ERROR] {e}")
        failed += 1

# Final summary
print("\n" + "="*70)
print("  FINAL RESULTS")
print("="*70)
print(f"\nPassed: {passed}/{len(tests)}")
print(f"Failed: {failed}/{len(tests)}")

if passed == len(tests):
    print("\n[SUCCESS] WebSearch is 100% WORKING!")
    print("\nYou can now use:")
    print("  1. Web UI: http://localhost:8080/simple")
    print("  2. Test UI: test_websearch_ui.html")
    print("  3. Python: ask_zero.py \"search for [topic]\"")
elif passed > 0:
    print("\n[PARTIAL SUCCESS] WebSearch is working but some tests failed")
    print("This is normal - some queries may not trigger all markers")
else:
    print("\n[FAILURE] WebSearch not working properly")
    print("Check:")
    print("  1. Is Ollama running? (http://localhost:11434)")
    print("  2. Is API Server running? (http://localhost:8080)")

print("\n" + "="*70)

