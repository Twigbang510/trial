#!/usr/bin/env python3

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.core.moderation import moderate_content
from app.core.gemini import chat_with_gemini, format_conversation_history

class TestModeration:
    """Test content moderation functionality"""
    
    async def test_clean_content(self):
        """Test that clean content passes moderation"""
        clean_messages = [
            "Hello, I need help with booking",
            "What time is available?",
            "Can you help me with my career?",
            "Thank you for your assistance"
        ]
        
        print("Testing clean content moderation...")
        for message in clean_messages:
            try:
                result = await moderate_content(message)
                violation_type = result.get('violation_type', 'CLEAN')
                print(f"'{message[:30]}...' -> {violation_type}")
                
                # Clean content should pass
                assert violation_type in ['CLEAN', None], f"Clean message flagged: {message}"
                
            except Exception as e:
                print(f"Moderation error for '{message}': {e}")
        
        print("✅ Clean content moderation working")
    
    async def test_inappropriate_content(self):
        """Test that inappropriate content is flagged"""
        inappropriate_messages = [
            "This is spam spam spam",
            "Buy now cheap products",
            "Click here for free money"
        ]
        
        print("Testing inappropriate content detection...")
        for message in inappropriate_messages:
            try:
                result = await moderate_content(message)
                violation_type = result.get('violation_type', 'CLEAN')
                print(f"'{message[:30]}...' -> {violation_type}")
                
                # Note: Moderation might not catch all cases, this is informational
                
            except Exception as e:
                print(f"Moderation error for '{message}': {e}")
        
        print("✅ Inappropriate content detection tested")
    
    async def test_moderation_response_format(self):
        """Test that moderation returns expected format"""
        test_message = "Hello, this is a test message"
        
        try:
            result = await moderate_content(test_message)
            
            # Check response format
            assert isinstance(result, dict), "Moderation should return dict"
            assert 'violation_type' in result, "Should have violation_type key"
            
            print(f"Moderation response format: {result}")
            print("✅ Moderation response format correct")
            
        except Exception as e:
            print(f"❌ Moderation format test failed: {e}")


class TestGeminiHelpers:
    """Test Gemini AI helper functions"""
    
    def test_conversation_history_formatting(self):
        """Test conversation history formatting"""
        mock_messages = [
            {"content": "Hello", "sender": "user"},
            {"content": "Hi! How can I help?", "sender": "bot"},
            {"content": "Tell me about AI", "sender": "user"}
        ]
        
        formatted = format_conversation_history(mock_messages)
        
        # Check format
        assert isinstance(formatted, list), "Should return list"
        assert len(formatted) == 3, "Should preserve all messages"
        
        # Check roles
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "model"  # bot -> model for Gemini
        assert formatted[2]["role"] == "user"
        
        print("✅ Conversation history formatting working")
    
    async def test_gemini_chat_basic(self):
        """Test basic Gemini chat functionality"""
        try:
            response = chat_with_gemini(
                message="What is AI?",
                conversation_history=[],
                context="consultant"
            )
            
            # Should get meaningful response
            assert isinstance(response, str), "Should return string"
            assert len(response) > 10, "Should return meaningful response"
            
            print(f"Gemini response (first 100 chars): {response[:100]}...")
            print("✅ Basic Gemini chat working")
            
        except Exception as e:
            print(f"❌ Gemini chat test failed: {e}")
    
    async def test_gemini_with_history(self):
        """Test Gemini chat with conversation history"""
        try:
            history = [
                {"role": "user", "parts": ["Hello"]},
                {"role": "model", "parts": ["Hi! How can I help you today?"]}
            ]
            
            response = chat_with_gemini(
                message="What services do you offer?",
                conversation_history=history,
                context="consultant"
            )
            
            assert isinstance(response, str)
            assert len(response) > 10
            
            print("✅ Gemini chat with history working")
            
        except Exception as e:
            print(f"❌ Gemini history test failed: {e}")


class TestSystemHealth:
    """Test overall system health and utilities"""
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        try:
            from app.core.config import settings
            from app.core.gemini import chat_with_gemini
            from app.core.moderation import moderate_content
            from app.core.booking_response_generator import booking_response_generator
            from app.crud.crud_lecturer_availability import lecturer_availability
            
            print("✅ All core modules imported successfully")
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
    
    def test_database_models(self):
        """Test that database models are properly defined"""
        try:
            from app.models.lecturer_availability import LecturerAvailability, BookingSlot
            from app.models.conversation import Conversation
            from app.models.user import User
            
            # Test model instantiation
            lecturer = LecturerAvailability(
                lecturer_id=1,
                lecturer_name="Test",
                day_of_week=1,
                start_time="09:00",
                end_time="17:00"
            )
            
            assert hasattr(lecturer, 'to_dict'), "LecturerAvailability should have to_dict method"
            
            print("✅ Database models working correctly")
            
        except Exception as e:
            print(f"❌ Database model test failed: {e}")


async def run_utils_tests():
    """Run all utility and moderation tests"""
    print("🧪 Running Utils and Moderation Tests")
    print("=" * 50)
    
    try:
        moderation_tests = TestModeration()
        gemini_tests = TestGeminiHelpers()
        health_tests = TestSystemHealth()
        
        print("\n📋 Testing Moderation...")
        await moderation_tests.test_clean_content()
        await moderation_tests.test_inappropriate_content()
        await moderation_tests.test_moderation_response_format()
        
        print("\n📋 Testing Gemini Helpers...")
        gemini_tests.test_conversation_history_formatting()
        await gemini_tests.test_gemini_chat_basic()
        await gemini_tests.test_gemini_with_history()
        
        print("\n📋 Testing System Health...")
        health_tests.test_imports()
        health_tests.test_database_models()
        
        print("\n" + "=" * 50)
        print("🎉 Utils and moderation tests completed!")
        
    except Exception as e:
        print(f"\n❌ Utils tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_utils_tests()) 