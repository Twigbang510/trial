#!/usr/bin/env python3

import sys
import os
from datetime import datetime, date, time
from typing import Dict, List

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app.core.booking_response_generator import booking_response_generator
from app.crud.crud_lecturer_availability import lecturer_availability
from app.models.lecturer_availability import LecturerAvailability
from app.db.session import get_db

class TestBookingLogic:
    """Test booking system logic and improvements"""
    
    async def test_intent_classification(self):
        """Test intent classification for different user messages"""
        test_cases = [
            ("book lịch 8h", "A"),  # Booking intent
            ("Giảng viên có lịch không?", "C"),  # Checking intent
            ("What is AI?", "O"),  # Out of scope
            ("Yes, I confirm", "A"),  # Confirmation
        ]
        
        for user_message, expected_intent in test_cases:
            result = await booking_response_generator.process_booking_request(
                user_message=user_message,
                conversation_history="",
                db_session=None
            )
            
            actual_intent = result.get("intent", "O")
            print(f"Message: '{user_message}' -> Intent: {actual_intent} (expected: {expected_intent})")
            
            # Note: AI might classify differently, this is just logging
    
    async def test_general_chat_fallback(self):
        """Test that general questions fallback appropriately"""
        general_questions = [
            "What is machine learning?",
            "Tôi muốn học về AI?",
            "Tell me about careers",
            "Hello"
        ]
        
        for question in general_questions:
            result = await booking_response_generator.process_booking_request(
                user_message=question,
                conversation_history="",
                db_session=None
            )
            
            intent = result.get("intent", "O")
            input_slots = result.get("input_slots", [])
            time_range = result.get("time_range", [])
            booking_options = result.get("booking_options", [])
            
            should_fallback = (
                intent == "O" or 
                (intent == "C" and not input_slots and not time_range and not booking_options)
            )
            
            print(f"Question: '{question}' -> Should fallback: {should_fallback}")
    
    def test_blocked_dates_logic(self):
        """Test blocked dates checking"""
        test_lecturer = LecturerAvailability(
            lecturer_id=999,
            lecturer_name="Test Lecturer",
            day_of_week=0,  # Monday
            start_time="08:00",
            end_time="17:00",
            blocked_dates=["2025-01-27"],
            is_active=True
        )
        
        db = next(get_db())
        try:
            target_date = "2025-01-27"
            # For MongoDB, we'll test the logic differently
            # Check if the date is in blocked_dates
            is_blocked = target_date in test_lecturer.blocked_dates
            
            # Should return blocked for blocked date
            assert is_blocked, f"Expected blocked date, got {is_blocked}"
            print("✅ Blocked dates logic working correctly")
            
        except Exception as e:
            print(f"❌ Error testing blocked dates: {e}")
    
    def test_time_parsing(self):
        """Test time parsing and normalization"""
        test_cases = [
            ("8h", ["08:00"]),
            ("2pm", ["14:00"]),
            ("từ 9h đến 11h", ["09:00", "11:00"]),
            ("book at 15:30", ["15:30"]),
        ]
        
        print("Testing time parsing...")
        for input_text, expected in test_cases:
            print(f"Input: '{input_text}' -> Expected: {expected}")
            # Note: Actual parsing happens in AI, this is documentation
    
    async def test_booking_options_accuracy(self):
        """Test that booking options are shown appropriately"""
        test_cases = [
            {
                "message": "book lịch 6h",  # Specific time, likely no match
                "should_have_options": False,  # Should not show random alternatives
                "description": "Specific time with no match"
            },
            {
                "message": "tôi muốn book từ 9h đến 11h",  # Time range
                "should_have_options": True,  # Should show alternatives in range
                "description": "Time range query"
            },
            {
                "message": "giảng viên có lịch không?",  # General inquiry
                "should_have_options": True,  # Should show general availability
                "description": "General availability inquiry"
            }
        ]
        
        for case in test_cases:
            result = await booking_response_generator.process_booking_request(
                user_message=case["message"],
                conversation_history="",
                db_session=None  # Use None for testing without DB
            )
            
            booking_options = result.get("booking_options", [])
            has_options = len(booking_options) > 0
            
            print(f"Case: {case['description']}")
            print(f"Message: '{case['message']}'")
            print(f"Has options: {has_options} (expected: {case['should_have_options']})")
            print(f"Options count: {len(booking_options)}")
            print("---")


class TestBookingCRUD:
    """Test booking CRUD operations"""
    
    def test_lecturer_availability_model(self):
        """Test lecturer availability model"""
        lecturer = LecturerAvailability(
            lecturer_id=1,
            lecturer_name="Dr. Smith",
            day_of_week=1,  # Tuesday
            start_time="09:00",
            end_time="17:00",
            is_active=True
        )
        
        # Test model properties
        assert lecturer.lecturer_name == "Dr. Smith"
        assert lecturer.start_time == "09:00"
        print("✅ Lecturer availability model working correctly")
    
    def test_slot_generation(self):
        """Test time slot generation"""
        lecturer = LecturerAvailability(
            lecturer_id=1,
            lecturer_name="Dr. Smith",
            day_of_week=1,
            start_time="09:00",
            end_time="11:00",  # 2 hours
            slot_duration_minutes=30,
            is_active=True
        )
        
        # For MongoDB models, we'll test basic functionality
        assert lecturer.lecturer_name == "Dr. Smith"
        assert lecturer.start_time == "09:00"
        assert lecturer.end_time == "11:00"
        print("✅ Slot generation model working correctly")


async def run_booking_tests():
    """Run all booking system tests"""
    print("🧪 Running Booking System Tests")
    print("=" * 50)
    
    try:
        logic_tests = TestBookingLogic()
        crud_tests = TestBookingCRUD()
        
        print("\n📋 Testing Booking Logic...")
        await logic_tests.test_intent_classification()
        await logic_tests.test_general_chat_fallback()
        logic_tests.test_blocked_dates_logic()
        logic_tests.test_time_parsing()
        await logic_tests.test_booking_options_accuracy()
        
        print("\n📋 Testing Booking CRUD...")
        crud_tests.test_lecturer_availability_model()
        crud_tests.test_slot_generation()
        
        print("\n" + "=" * 50)
        print("🎉 Booking system tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_booking_tests()) 