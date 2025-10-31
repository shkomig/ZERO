#!/usr/bin/env python3
"""
Test RTX 5090 Performance Optimizations
"""
import requests
import time
import json

def test_rtx_performance():
    """Test performance with RTX 5090 optimizations"""
    base_url = "http://localhost:8080"
    
    print("Testing RTX 5090 Performance Optimizations...")
    
    # Test 1: Basic chat with expert model
    print("\n1. Testing Expert Model (Mixtral 8x7b)...")
    t0 = time.time()
    try:
        r = requests.post(f"{base_url}/api/chat", json={
            "message": "Test RTX 5090 performance with Hebrew text",
            "model": "expert"
        }, timeout=30)
        dur = time.time() - t0
        
        print(f"   STATUS: {r.status_code}")
        print(f"   DURATION: {round(dur, 2)} seconds")
        if r.status_code == 200:
            js = r.json()
            print(f"   MODEL USED: {js.get('model_used', 'unknown')}")
            print(f"   RESPONSE LENGTH: {len(js.get('response', ''))}")
            print(f"   RESPONSE PREVIEW: {js.get('response', '')[:100]}...")
        else:
            print(f"   ERROR: {r.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 2: Multi-model workflow
    print("\n2. Testing Multi-Model Workflow...")
    t0 = time.time()
    try:
        r = requests.post(f"{base_url}/api/chat/auto", json={
            "task": "Create a simple Python function to calculate fibonacci numbers",
            "verbose": False
        }, timeout=60)
        dur = time.time() - t0
        
        print(f"   STATUS: {r.status_code}")
        print(f"   DURATION: {round(dur, 2)} seconds")
        if r.status_code == 200:
            js = r.json()
            print(f"   MODE: {js.get('mode', 'unknown')}")
            print(f"   MODELS USED: {js.get('models_used', [])}")
            print(f"   RESULT PREVIEW: {js.get('final_result', '')[:150]}...")
        else:
            print(f"   ERROR: {r.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test 3: Concurrent requests (test MAX_CONCURRENT_LLM=4)
    print("\n3. Testing Concurrent Requests...")
    import concurrent.futures
    
    def single_request(i):
        try:
            t0 = time.time()
            r = requests.post(f"{base_url}/api/chat", json={
                "message": f"Test concurrent request {i}",
                "model": "fast"
            }, timeout=20)
            dur = time.time() - t0
            return {"id": i, "status": r.status_code, "duration": dur}
        except Exception as e:
            return {"id": i, "error": str(e)}
    
    t0 = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(single_request, i) for i in range(4)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    total_dur = time.time() - t0
    
    print(f"   TOTAL DURATION: {round(total_dur, 2)} seconds")
    for result in results:
        if "error" in result:
            print(f"   Request {result['id']}: ERROR - {result['error']}")
        else:
            print(f"   Request {result['id']}: {result['status']} in {round(result['duration'], 2)}s")
    
    print("\nRTX 5090 Performance Test Complete!")

if __name__ == "__main__":
    test_rtx_performance()
