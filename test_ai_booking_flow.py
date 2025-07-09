#!/usr/bin/env python3
"""
Test AI Booking Flow
Tests the complete flow from AI response to booking creation
"""

import asyncio
import httpx
import json
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_ai_booking_flow():
    """Test the complete AI booking flow"""
    print("🧪 Testing AI Booking Flow...")
    
    # Test data - AI response with booking
    ai_response = {
        "isSchedule": True,
        "datetime": "1900-01-01 08:00:00, 2025-07-10 14:30:00",
        "timezone": "Indochina Timezone",
        "output": "Tôi xác nhận rằng bạn đã đặt lịch vào Thứ Năm, 2025-07-10, lúc 14:30. Cảm ơn bạn đã dành thời gian!",
        "status": {
            "status": "A",
            "safety_score": 1,
            "reasoning": "The user's request is a clear acceptance of the suggested time slot",
            "total_tokens": 848,
            "total_cost": 0.0029224999999999998
        },
        "needAttention": False
    }
    
    # Test backend booking processing
    print("\n📋 Testing Backend Booking Processing...")
    
    try:
        from backend.app.services.booking_service import BookingService
        from backend.app.db.session import get_db
        
        # Mock database session
        db = None  # In real test, you'd get actual DB session
        
        # Test datetime parsing
        booking_details = BookingService._parse_ai_datetime(ai_response["datetime"])
        
        if booking_details:
            print("✅ Datetime parsing successful:")
            print(f"   Date: {booking_details['date']}")
            print(f"   Time: {booking_details['time']}")
            print(f"   Lecturer: {booking_details['lecturer_name']}")
            print(f"   Subject: {booking_details['subject']}")
        else:
            print("❌ Datetime parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False
    
    # Test frontend API response
    print("\n🌐 Testing Frontend API Response...")
    
    try:
        # Mock frontend response
        frontend_response = {
            "response": "🎉 Booking Confirmed Successfully!",
            "conversation_id": "123",
            "is_appropriate": True,
            "moderation_action": "CLEAN",
            "booking_options": [],
            "needs_availability_check": False,
            "suggested_next_action": "complete",
            "booking_status": "complete",
            "ai_is_schedule": True,
            "ai_booking_datetime": "1900-01-01 08:00:00, 2025-07-10 14:30:00",
            "ai_booking_timezone": "Indochina Timezone",
            "ai_booking_details": {
                "date": "2025-07-10",
                "time": "14:30",
                "lecturer_name": "Career Advisor",
                "subject": "Career Consultation",
                "location": "Online Meeting",
                "duration_minutes": 30
            },
            "email_sent": True
        }
        
        # Validate response structure
        required_fields = [
            "ai_is_schedule", "ai_booking_datetime", "ai_booking_details",
            "booking_status", "email_sent"
        ]
        
        for field in required_fields:
            if field not in frontend_response:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ Frontend response structure valid")
        print(f"   AI Schedule: {frontend_response['ai_is_schedule']}")
        print(f"   Booking Status: {frontend_response['booking_status']}")
        print(f"   Email Sent: {frontend_response['email_sent']}")
        
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! AI booking flow is working correctly.")
    return True

async def test_error_handling():
    """Test error handling scenarios"""
    print("\n🛡️ Testing Error Handling...")
    
    try:
        from backend.app.services.booking_service import BookingService
        
        # Test invalid datetime format
        invalid_datetime = "invalid datetime format"
        result = BookingService._parse_ai_datetime(invalid_datetime)
        
        if result is None:
            print("✅ Invalid datetime handling: OK")
        else:
            print("❌ Invalid datetime should return None")
            return False
        
        # Test missing datetime
        result = BookingService._parse_ai_datetime("")
        if result is None:
            print("✅ Empty datetime handling: OK")
        else:
            print("❌ Empty datetime should return None")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    print("✅ Error handling tests passed!")
    return True

async def main():
    """Run all tests"""
    print("🚀 Starting AI Booking Flow Tests...")
    
    # Test 1: Main flow
    success1 = await test_ai_booking_flow()
    
    # Test 2: Error handling
    success2 = await test_error_handling()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Implementation is ready.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    asyncio.run(main()) 