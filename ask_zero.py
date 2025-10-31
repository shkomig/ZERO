import sys
import requests


def ask_zero(message: str):
    url = "http://localhost:8080/api/chat"
    payload = {"message": message, "use_memory": True}
    try:
        resp = requests.post(url, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        print(data.get("response", ""))
    except Exception as e:
        print(f"Error calling Zero: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ask_zero.py \"השאלה שלך\"")
        sys.exit(1)
    ask_zero(" ".join(sys.argv[1:]))


