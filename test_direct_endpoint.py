#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the direct Agent Orchestrator endpoint"""
import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

url = 'http://localhost:8080/api/agent/direct'
payload = {"message": "צור פרויקט Python חדש בשם myapp", "use_memory": False}

print("=" * 70)
print("Testing DIRECT Agent Orchestrator Endpoint")
print("=" * 70)
print(f"URL: {url}")
print(f"Payload: {payload}")
print("=" * 70)

try:
    response = requests.post(url, json=payload, timeout=120)
    result = response.json()
    
    print(f"\nStatus: {response.status_code}")
    print(f"Model: {result.get('model_used', 'N/A')}")
    print(f"\nResponse:\n{result.get('response', 'N/A')}")
    print("=" * 70)
    
    # Check if files were created
    import os
    if os.path.exists('workspace/myapp'):
        print("\nSUCCESS: Directory 'workspace/myapp' created!")
        if os.path.exists('workspace/myapp/README.md'):
            print("  - README.md exists")
            with open('workspace/myapp/README.md', 'r', encoding='utf-8') as f:
                print(f"    Content: {f.read()[:100]}...")
        if os.path.exists('workspace/myapp/main.py'):
            print("  - main.py exists")
            with open('workspace/myapp/main.py', 'r', encoding='utf-8') as f:
                print(f"    Content: {f.read()[:100]}...")
    else:
        print("\nFAILED: Directory 'workspace/myapp' NOT created")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    print(traceback.format_exc())

