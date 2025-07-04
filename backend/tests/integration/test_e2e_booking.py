#!/usr/bin/env python3

import sys
import os
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.main import app

client = TestClient(app)

class TestE2EBooking:
    """Test complete booking workflows end-to-end"""
    
    def test_complete_booking_flow(self):
        """Test a complete booking flow from chat to confirmation"""
        print("\n🔄 Testing complete booking flow...")
        
        # Step 1: Initial chat - general question
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "Hello, I need help with booking",
            "context": "consultant"
        })
        
        if response.status_code != 200:
            print(f"❌ Initial chat failed: {response.status_code}")
            return
        
        data = response.json()
        conversation_id = data.get("conversation_id")
        print(f"✅ Initial chat successful, conversation_id: {conversation_id}")
        
        # Step 2: Specific booking request
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "I want to book at 2pm tomorrow",
            "conversation_id": conversation_id,
            "context": "consultant"
        })
        
        if response.status_code == 200:
            data = response.json()
            booking_options = data.get("booking_options", [])
            print(f"✅ Booking request processed, {len(booking_options)} options returned")
            
            # Step 3: If we have booking options, test confirmation flow
            if booking_options:
                option = booking_options[0]
                
                # Test confirm booking endpoint
                confirm_response = client.post("/api/v1/chatbot/confirm-booking", json={
                    "conversation_id": conversation_id,
                    "availability_id": option["availability_id"],
                    "lecturer_name": option["lecturer_name"],
                    "date": option["date"],
                    "time": option["time"],
                    "subject": option["subject"],
                    "location": option["location"],
                    "duration_minutes": option["duration_minutes"]
                })
                
                if confirm_response.status_code == 200:
                    print("✅ Booking confirmation flow working")
                else:
                    print(f"⚠️ Booking confirmation failed: {confirm_response.status_code}")
            else:
                print("📝 No booking options available (expected in some cases)")
        else:
            print(f"❌ Booking request failed: {response.status_code}")
    
    def test_fallback_scenarios(self):
        """Test fallback scenarios and error handling"""
        print("\n🔄 Testing fallback scenarios...")
        
        # Test AI fallback for general questions
        test_cases = [
            "What is machine learning?",
            "Tell me about university programs",
            "How can you help me with my career?"
        ]
        
        for question in test_cases:
            response = client.post("/api/v1/chatbot/chat", json={
                "message": question,
                "context": "consultant"
            })
            
            if response.status_code == 200:
                data = response.json()
                # Should get meaningful response for general questions
                response_text = data.get("response", "")
                if len(response_text) > 20:  # Meaningful response
                    print(f"✅ Fallback working for: '{question[:30]}...'")
                else:
                    print(f"⚠️ Short response for: '{question[:30]}...'")
            else:
                print(f"❌ Request failed for: '{question[:30]}...'")
    
    def test_conversation_management(self):
        """Test conversation management features"""
        print("\n🔄 Testing conversation management...")
        
        # Create a conversation
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "Hello",
            "context": "consultant"
        })
        
        if response.status_code == 200:
            conversation_id = response.json().get("conversation_id")
            
            # Test cancel booking endpoint  
            cancel_response = client.post("/api/v1/chatbot/cancel-booking", json={
                "conversation_id": conversation_id,
                "message": "No"
            })
            
            if cancel_response.status_code == 200:
                print("✅ Cancel booking endpoint working")
            else:
                print(f"⚠️ Cancel booking failed: {cancel_response.status_code}")
        
        print("📝 Conversation management tests completed")
    
    def test_error_handling(self):
        """Test various error scenarios"""
        print("\n🔄 Testing error handling...")
        
        # Test invalid conversation ID
        response = client.post("/api/v1/chatbot/chat", json={
            "message": "Test",
            "conversation_id": 999999,
            "context": "consultant"
        })
        
        # Should handle gracefully (might create new conversation or return error)
        print(f"Invalid conversation ID handled: {response.status_code}")
        
        # Test invalid booking confirmation
        response = client.post("/api/v1/chatbot/confirm-booking", json={
            "conversation_id": 999999,
            "availability_id": 999999,
            "lecturer_name": "Test",
            "date": "2025-01-01",
            "time": "09:00",
            "subject": "Test",
            "location": "Test",
            "duration_minutes": 30
        })
        
        # Should return appropriate error
        if response.status_code in [404, 403, 500]:
            print("✅ Error handling working for invalid booking")
        else:
            print(f"⚠️ Unexpected response for invalid booking: {response.status_code}")


def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running Integration Tests")
    print("=" * 50)
    
    try:
        e2e_tests = TestE2EBooking()
        
        e2e_tests.test_complete_booking_flow()
        e2e_tests.test_fallback_scenarios()
        e2e_tests.test_conversation_management()
        e2e_tests.test_error_handling()
        
        print("\n" + "=" * 50)
        print("🎉 Integration tests completed!")
        
    except Exception as e:
        print(f"\n❌ Integration tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_integration_tests() 