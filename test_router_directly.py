#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Router Directly - Bypass API to test routing logic
"""
import sys
sys.path.insert(0, '.')

from router_context_aware import ContextAwareRouter
from streaming_llm import StreamingMultiModelLLM

print("="*70)
print("  Testing Router Logic Directly")
print("="*70)

# Initialize
llm = StreamingMultiModelLLM()
router = ContextAwareRouter(llm)

# Test queries
test_queries = [
    "search for latest AI news",
    "what is the current price of NVDA?",
    "latest news about SpaceX",
    "who is Elon Musk?",
    "current weather in New York",
    "price of AAPL stock"
]

print("\nTesting routing decisions...\n")

for query in test_queries:
    result = router.route_with_reasoning(query)
    model = result['model']
    
    # Expected: all should be "fast"
    expected = "fast"
    status = "PASS" if model == expected else "FAIL"
    
    print(f"[{status}] Query: {query[:50]}")
    print(f"      Model: {model} (expected: {expected})")
    print(f"      Reason: {result.get('reasoning', 'N/A')[:80]}")
    print()

print("="*70)
print("If all show PASS, restart API server to apply changes")
print("If any show FAIL, router logic needs more adjustment")
print("="*70)

