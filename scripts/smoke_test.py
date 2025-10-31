import requests
import time


def main():
    base = "http://localhost:8080"

    # Test 1: simple chat
    t0 = time.time()
    r = requests.post(base + "/api/chat", json={"message": "quick ping", "use_memory": True})
    t1 = time.time() - t0
    j = r.json()
    print("CHAT_STATUS", r.status_code)
    print("CHAT_MODEL", j.get("model_used"))
    print("CHAT_DURATION", round(t1, 2))
    print("CHAT_SNIPPET", (j.get("response", "")[:120]).replace("\n", " "))

    # Test 2: multi-model auto
    t0 = time.time()
    r2 = requests.post(
        base + "/api/chat/auto",
        json={"task": "Design a simple strategy and implement Python code to demo it", "verbose": False},
    )
    t2 = time.time() - t0
    j2 = r2.json()
    print("AUTO_STATUS", r2.status_code)
    print("AUTO_MODE", j2.get("mode"))
    print("AUTO_MODELS", j2.get("models_used"))
    print("AUTO_DURATION", round(t2, 2))
    print("AUTO_RESULT_SNIPPET", (j2.get("final_result", "")[:120]).replace("\n", " "))


if __name__ == "__main__":
    main()


