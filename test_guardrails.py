#!/usr/bin/env python3
"""
Test Enhanced Guardrails
"""
import requests
import json

def test_guardrails():
    """Test enhanced security guardrails"""
    base_url = "http://localhost:8080"
    
    print("Testing Enhanced Guardrails...")
    
    # Test 1: Database Guardrails
    print("\n1. Testing Database Guardrails...")
    
    # Test dangerous DELETE without WHERE
    try:
        r = requests.post(f"{base_url}/api/tools/database", json={
            "action": "query",
            "query": "DELETE FROM users",
            "db_path": "test.db"
        })
        print(f"   DELETE without WHERE: {r.status_code} - {r.json().get('error', 'OK')}")
    except Exception as e:
        print(f"   DELETE without WHERE: ERROR - {e}")
    
    # Test SELECT without LIMIT
    try:
        r = requests.post(f"{base_url}/api/tools/database", json={
            "action": "query",
            "query": "SELECT * FROM users",
            "db_path": "test.db"
        })
        print(f"   SELECT without LIMIT: {r.status_code} - {r.json().get('error', 'OK')}")
    except Exception as e:
        print(f"   SELECT without LIMIT: ERROR - {e}")
    
    # Test 2: Bash Guardrails
    print("\n2. Testing Bash Guardrails...")
    
    # Test dangerous command
    try:
        r = requests.post(f"{base_url}/api/tools/execute", json={
            "action": "bash",
            "command": "rm -rf /"
        })
        print(f"   Dangerous rm command: {r.status_code} - {r.json().get('error', 'OK')}")
    except Exception as e:
        print(f"   Dangerous rm command: ERROR - {e}")
    
    # Test allowed command
    try:
        r = requests.post(f"{base_url}/api/tools/execute", json={
            "action": "bash",
            "command": "echo Hello World"
        })
        print(f"   Allowed echo command: {r.status_code} - {r.json().get('result', 'ERROR')}")
    except Exception as e:
        print(f"   Allowed echo command: ERROR - {e}")
    
    # Test GPU monitoring command (should be allowed)
    try:
        r = requests.post(f"{base_url}/api/tools/execute", json={
            "action": "bash",
            "command": "nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv"
        })
        print(f"   GPU monitoring command: {r.status_code} - {r.json().get('result', 'ERROR')}")
    except Exception as e:
        print(f"   GPU monitoring command: ERROR - {e}")
    
    print("\nGuardrails Test Complete!")

if __name__ == "__main__":
    test_guardrails()




