#!/usr/bin/env python3
"""
Quick test script to check each component individually
"""
import httpx
import json
import asyncio

async def test_backend_health():
    """Test backend health"""
    print("🔍 Testing Backend Health...")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Backend Health: OK")
                return True
            else:
                print(f"❌ Backend Health: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Backend Health: {e}")
        return False

async def test_ai_module():
    """Test AI module directly"""
    print("🔍 Testing AI Module...")
    try:
        payload = {
            "question": "Xin chào",
            "channel": "SMS",
            "chat_history": [],
            "contact_id": "123"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("http://localhost:80/trial-ai/v1/kb_response", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ AI Module: OK")
                print(f"   Response: {data.get('output', 'No output field')}")
                return True
            else:
                print(f"❌ AI Module: HTTP {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ AI Module: {e}")
        print("   💡 Make sure AI module is running: uvicorn server:app --host 0.0.0.0 --port 80")
        return False

async def test_backend_proxy():
    """Test backend proxy"""
    print("🔍 Testing Backend Proxy...")
    try:
        payload = {
            "question": "Test message",
            "channel": "SMS",
            "chat_history": [],
            "contact_id": "123"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("http://localhost:8000/api/v1/chatbot/ai/kb_response", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Backend Proxy: OK")
                return True
            else:
                print(f"❌ Backend Proxy: HTTP {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Backend Proxy: {e}")
        return False

async def test_chat_endpoint():
    """Test main chat endpoint"""
    print("🔍 Testing Chat Endpoint...")
    try:
        payload = {
            "message": "Xin chào",
            "conversation_id": None,
            "context": "consultant"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post("http://localhost:8000/api/v1/chatbot/chat", json=payload)
            if response.status_code == 200:
                data = response.json()
                print("✅ Chat Endpoint: OK")
                print(f"   Response: {data.get('response', 'No response field')}")
                return True
            else:
                print(f"❌ Chat Endpoint: HTTP {response.status_code} - {response.text}")
                return False
    except Exception as e:
        print(f"❌ Chat Endpoint: {e}")
        return False

async def main():
    print("🚀 Quick Chat Flow Test")
    print("=" * 50)
    
    results = []
    
    # Test each component
    results.append(await test_backend_health())
    results.append(await test_ai_module())
    results.append(await test_backend_proxy())
    results.append(await test_chat_endpoint())
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        
        if not results[0]:  # Backend health failed
            print("\n💡 Backend Health Failed:")
            print("   - Make sure backend is running on port 8000")
            print("   - Check backend logs for errors")
            
        if not results[1]:  # AI module failed
            print("\n💡 AI Module Failed:")
            print("   - Make sure AI module is running: uvicorn server:app --host 0.0.0.0 --port 80")
            print("   - Check AI module logs for errors")
            print("   - Verify AI module can handle the payload format")
            
        if not results[2]:  # Backend proxy failed
            print("\n💡 Backend Proxy Failed:")
            print("   - Check if backend can connect to AI module")
            print("   - Verify AI_MODULE_URL in backend config")
            
        if not results[3]:  # Chat endpoint failed
            print("\n💡 Chat Endpoint Failed:")
            print("   - Check chat endpoint implementation")
            print("   - Verify payload mapping between backend and AI module")

if __name__ == "__main__":
    asyncio.run(main()) 