import httpx
import json

AI_MODULE_URL = "http://localhost:80/trial-ai/v1/kb_response"

def main():
    payload = {
        "message": "Hello, can you help me with booking an appointment?",
        "conversation_id": "test_conv_123",
        "history": "Previous conversation history here",
        "context": "consultant"
    }
    print(f"Sending to {AI_MODULE_URL}:")
    print(json.dumps(payload, indent=2))
    with httpx.Client(timeout=30.0) as client:
        response = client.post(AI_MODULE_URL, json=payload)
        print(f"Status code: {response.status_code}")
        try:
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print("Raw response:")
            print(response.text)

if __name__ == "__main__":
    main() 