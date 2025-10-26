#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct API test to see orchestrator in action"""
import requests
import json
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def test_create_project():
    """Test creating a project"""
    url = 'http://localhost:8080/api/chat'
    payload = {
        "message": "צור פרויקט Python חדש בשם myapp",
        "use_memory": True
    }
    
    print("=" * 70)
    print("Sending request to Zero Agent:")
    print(f"Message: {payload['message']}")
    print("=" * 70)
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        result = response.json()
        
        print("\n" + "=" * 70)
        print("RESPONSE RECEIVED:")
        print("=" * 70)
        print(f"Status Code: {response.status_code}")
        print(f"Model Used: {result.get('model_used', 'N/A')}")
        print(f"\nResponse:\n{result.get('response', 'N/A')}")
        print("=" * 70)
        
        # Check if project was created
        import os
        if os.path.exists('workspace/myapp'):
            print("\n✅ SUCCESS: Project directory 'workspace/myapp' was created!")
            if os.path.exists('workspace/myapp/README.md'):
                print("✅ README.md exists")
            if os.path.exists('workspace/myapp/main.py'):
                print("✅ main.py exists")
        else:
            print("\n❌ FAILED: Project directory 'workspace/myapp' was NOT created")
            print("This means the Agent Orchestrator did not execute the action.")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Is it running on port 8080?")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_create_project()

