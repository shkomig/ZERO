#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick Test - Perplexity Integration
"""
import os
import sys

# Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("="*70)
print("  Perplexity Integration - Quick Test")
print("="*70)

# Check 1: .env file exists
print("\n[1/4] Checking .env file...")
if os.path.exists('.env'):
    print("     ✓ .env exists")
    
    # Read and check for API key
    with open('.env', 'r') as f:
        content = f.read()
        if 'PERPLEXITY_API_KEY' in content:
            if 'your_perplexity_key_here' in content or 'pplx-' not in content:
                print("     ⚠ .env exists but API key needs to be set!")
                print("     → Open .env and replace with your actual key")
            else:
                print("     ✓ PERPLEXITY_API_KEY found in .env")
        else:
            print("     ⚠ PERPLEXITY_API_KEY not found in .env")
            print("     → Add: PERPLEXITY_API_KEY=your_key_here")
else:
        print("     [ERROR] .env NOT FOUND")
        print("     → Create .env file with your Perplexity API key")

# Check 2: Environment variable loaded
print("\n[2/4] Checking environment variable...")
api_key = os.getenv('PERPLEXITY_API_KEY')
if api_key:
    if 'pplx-' in api_key and len(api_key) > 20:
        masked_key = api_key[:10] + "..." + api_key[-5:] if len(api_key) > 15 else "***"
        print(f"     [OK] Loaded: {masked_key}")
    else:
        print("     [WARNING] Key format looks invalid")
else:
    print("     [ERROR] Not loaded")
    print("     → Make sure .env file is in project root")

# Check 3: Tool files exist
print("\n[3/4] Checking tool files...")
files = [
    'tool_perplexity_search.py',
    'tool_websearch_improved.py'
]
for file in files:
    if os.path.exists(file):
        print(f"     ✓ {file}")
    else:
        print(f"     ✗ {file} NOT FOUND")

# Check 4: Test Perplexity (if key available)
print("\n[4/4] Testing Perplexity...")
if api_key and 'pplx-' in api_key:
    try:
        from tool_perplexity_search import PerplexitySearchTool
        
        tool = PerplexitySearchTool()
        result = tool.search("What is 2+2?", model='fast')
        
        if result.get('success'):
            print("     [SUCCESS] Perplexity API is working!")
            print(f"     Answer: {result['answer'][:80]}...")
        else:
            print(f"     [ERROR] {result.get('error')}")
    except Exception as e:
        print(f"     ✗ Error: {e}")
else:
    print("     ⚠ Skipped (no valid API key)")

# Summary
print("\n" + "="*70)
print("  Summary")
print("="*70)

if api_key and 'pplx-' in api_key:
    print("\n✅ Perplexity is configured and ready!")
    print("\nNext steps:")
    print("  1. Restart API Server: python api_server.py")
    print("  2. Look for: '[WebSearch] ✓ Perplexity AI enabled'")
    print("  3. Ask questions with 'latest', 'who is', 'explain', etc.")
else:
    print("\n⚠ Perplexity not configured yet")
    print("\nTo configure:")
    print("  1. Create/edit .env file")
    print("  2. Add: PERPLEXITY_API_KEY=pplx-your-key-here")
    print("  3. Restart terminal/IDE")
    print("  4. Run this test again")

print("\n" + "="*70)

