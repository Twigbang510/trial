#!/usr/bin/env python3

import asyncio
import httpx
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

# Import AI_MODULE_URL from chatbot
from app.api.v1.chatbot import AI_MODULE_URL

async def test_ai_module_proxy():
    """Test the AI module proxy endpoint với message 'xin chào'"""
    
    test_payload = {
        "message": "xin chào",
        "context": "consultant",
        "conversation_id": "test-hello"
    }
    print("Testing AI Module Proxy với message 'xin chào'...")
    print(f"AI Module URL: {AI_MODULE_URL}")
    print(f"Test payload: {json.dumps(test_payload, indent=2)}")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(AI_MODULE_URL, json=test_payload)
            print(f"Status: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print(f"Response: {response.text}")
            if response.status_code == 200:
                data = response.json()
                print(f"Parsed JSON: {json.dumps(data, indent=2)}")
            else:
                print(f"Error response: {response.text}")
    except httpx.ConnectError as e:
        print(f"Connection error: {e}")
        print("AI module might not be running on the expected port")
    except httpx.TimeoutException as e:
        print(f"Timeout error: {e}")
        print("AI module is taking too long to respond")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_module_proxy()) 