#!/usr/bin/env python3
"""
Test script for chat flow between backend and AI module
"""
import asyncio
import httpx
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"
AI_MODULE_URL = "http://localhost:80"
TEST_USER_ID = "test_user_123"

class ChatFlowTester:
    def __init__(self):
        self.backend_url = BACKEND_URL
        self.ai_module_url = AI_MODULE_URL
        self.session = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=30.0)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    async def test_ai_module_direct(self) -> bool:
        """Test direct connection to AI module"""
        try:
            logger.info("Testing direct connection to AI module...")
            
            test_payload = {
                "message": "Hello, can you help me with booking an appointment?",
                "conversation_id": "test_conv_123",
                "history": "Previous conversation history here",
                "context": "consultant"
            }
            
            response = await self.session.post(
                f"{self.ai_module_url}/trial-ai/v1/kb_response",
                json=test_payload
            )
            
            if response.status_code == 200:
                logger.info("✅ AI module direct test PASSED")
                logger.debug(f"AI module response: {response.json()}")
                return True
            else:
                logger.error(f"❌ AI module direct test FAILED: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ AI module direct test FAILED with exception: {e}")
            return False
    
    async def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            logger.info("Testing backend health...")
            
            response = await self.session.get(f"{self.backend_url}/health")
            
            if response.status_code == 200:
                logger.info("✅ Backend health test PASSED")
                return True
            else:
                logger.error(f"❌ Backend health test FAILED: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backend health test FAILED with exception: {e}")
            return False
    
    async def test_backend_proxy_endpoint(self) -> bool:
        """Test backend proxy endpoint"""
        try:
            logger.info("Testing backend proxy endpoint...")
            
            test_payload = {
                "message": "Test message for proxy",
                "conversation_id": "test_conv_456",
                "history": "Test history",
                "context": "consultant"
            }
            
            response = await self.session.post(
                f"{self.backend_url}/api/v1/chatbot/ai/kb_response",
                json=test_payload
            )
            
            if response.status_code == 200:
                logger.info("✅ Backend proxy test PASSED")
                logger.debug(f"Proxy response: {response.json()}")
                return True
            else:
                logger.error(f"❌ Backend proxy test FAILED: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Backend proxy test FAILED with exception: {e}")
            return False
    
    async def test_chat_endpoint(self) -> bool:
        """Test the main chat endpoint"""
        try:
            logger.info("Testing main chat endpoint...")
            
            # First, we need to create a user or get an existing one
            # For testing, we'll use a simple chat request
            chat_payload = {
                "message": "Hello, I need help with booking an appointment",
                "conversation_id": None,  # Let backend create new conversation
                "context": "consultant"
            }
            
            response = await self.session.post(
                f"{self.backend_url}/api/v1/chatbot/chat",
                json=chat_payload
            )
            
            if response.status_code == 200:
                logger.info("✅ Chat endpoint test PASSED")
                response_data = response.json()
                logger.debug(f"Chat response: {json.dumps(response_data, indent=2)}")
                return True
            else:
                logger.error(f"❌ Chat endpoint test FAILED: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Chat endpoint test FAILED with exception: {e}")
            return False
    
    async def test_full_chat_flow(self) -> bool:
        """Test the complete chat flow"""
        try:
            logger.info("Testing complete chat flow...")
            
            # Test 1: Simple greeting
            chat_payload_1 = {
                "message": "Hi, how are you?",
                "conversation_id": None,
                "context": "consultant"
            }
            
            response1 = await self.session.post(
                f"{self.backend_url}/api/v1/chatbot/chat",
                json=chat_payload_1
            )
            
            if response1.status_code != 200:
                logger.error(f"❌ First chat message failed: {response1.status_code} - {response1.text}")
                return False
            
            response_data1 = response1.json()
            conversation_id = response_data1.get("conversation_id")
            logger.info(f"✅ First chat message successful. Conversation ID: {conversation_id}")
            
            # Test 2: Follow-up message in same conversation
            chat_payload_2 = {
                "message": "I want to book an appointment for next week",
                "conversation_id": conversation_id,
                "context": "consultant"
            }
            
            response2 = await self.session.post(
                f"{self.backend_url}/api/v1/chatbot/chat",
                json=chat_payload_2
            )
            
            if response2.status_code == 200:
                logger.info("✅ Second chat message successful")
                response_data2 = response2.json()
                logger.debug(f"Second response: {json.dumps(response_data2, indent=2)}")
                return True
            else:
                logger.error(f"❌ Second chat message failed: {response2.status_code} - {response2.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Full chat flow test FAILED with exception: {e}")
            return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting Chat Flow Tests...")
    
    async with ChatFlowTester() as tester:
        results = {}
        
        # Test 1: Backend health
        logger.info("\n" + "="*50)
        logger.info("TEST 1: Backend Health Check")
        results["backend_health"] = await tester.test_backend_health()
        
        # Test 2: AI module direct connection
        logger.info("\n" + "="*50)
        logger.info("TEST 2: AI Module Direct Connection")
        results["ai_module_direct"] = await tester.test_ai_module_direct()
        
        # Test 3: Backend proxy endpoint
        logger.info("\n" + "="*50)
        logger.info("TEST 3: Backend Proxy Endpoint")
        results["backend_proxy"] = await tester.test_backend_proxy_endpoint()
        
        # Test 4: Main chat endpoint
        logger.info("\n" + "="*50)
        logger.info("TEST 4: Main Chat Endpoint")
        results["chat_endpoint"] = await tester.test_chat_endpoint()
        
        # Test 5: Full chat flow
        logger.info("\n" + "="*50)
        logger.info("TEST 5: Full Chat Flow")
        results["full_chat_flow"] = await tester.test_full_chat_flow()
        
        # Summary
        logger.info("\n" + "="*50)
        logger.info("TEST RESULTS SUMMARY")
        logger.info("="*50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info(f"{test_name}: {status}")
            if result:
                passed += 1
        
        logger.info(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            logger.info("🎉 All tests passed! Chat flow is working correctly.")
        else:
            logger.error("⚠️  Some tests failed. Check the logs above for details.")
            
        return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 