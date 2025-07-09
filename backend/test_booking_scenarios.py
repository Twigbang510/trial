#!/usr/bin/env python3
"""
Booking Scenarios Test
Tests specific booking scenarios and edge cases
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.booking_response_generator import booking_response_generator
from app.db.session import get_db

class BookingScenariosTest:
    def __init__(self):
        self.test_results = []
        self.conversation_id = 1  # Mock conversation ID for testing
    
    async def test_scenario_1_normal_to_booking(self, db):
        """Scenario 1: Normal conversation -> Booking request"""
        print("\n🔄 Scenario 1: Normal conversation -> Booking request")
        
        messages = [
            "Hello, how are you?",
            "I need some information about universities",
            "I want to book a consultation"
        ]
        
        for i, message in enumerate(messages):
            print(f"   Step {i+1}: '{message}'")
            
            # Generate response
            response = await booking_response_generator.process_booking_request(
                user_message=message,
                conversation_history="",
                db_session=db
            )
            
            intent = response.get("intent", "")
            is_booking = intent in ["A", "B", "C"]
            has_options = bool(response.get("booking_options", []))
            
            print(f"     Intent: {intent}, Booking: {is_booking}, Options: {has_options}")
            
            # Store result
            self.test_results.append({
                "scenario": "Normal to Booking",
                "step": i+1,
                "message": message,
                "intent": intent,
                "is_booking": is_booking,
                "has_options": has_options,
                "expected_booking": i == 2,  # Only last message should be booking
                "passed": (i < 2 and not is_booking) or (i == 2 and is_booking)
            })
    
    async def test_scenario_2_time_selection(self, db):
        """Scenario 2: Time selection patterns"""
        print("\n⏰ Scenario 2: Time selection patterns")
        
        time_messages = [
            "I want to book at 9:00",
            "Book 14:00",
            "Tôi muốn book lúc 10h",
            "Can I book the 15:00 slot?",
            "Book 9:00 please",
            "Tôi rảnh vào lúc 8h"
        ]
        
        for i, message in enumerate(time_messages):
            print(f"   Test {i+1}: '{message}'")
            
            # Generate response
            response = await booking_response_generator.process_booking_request(
                user_message=message,
                conversation_history="",
                db_session=db
            )
            
            intent = response.get("intent", "")
            is_time_selection = intent == "C"
            has_confirmation = bool(response.get("awaiting_confirmation"))
            
            print(f"     Intent: {intent}, Time selection: {is_time_selection}, Confirmation: {has_confirmation}")
            
            # Store result
            self.test_results.append({
                "scenario": "Time Selection",
                "test": i+1,
                "message": message,
                "intent": intent,
                "is_time_selection": is_time_selection,
                "has_confirmation": has_confirmation,
                "expected": True,
                "passed": is_time_selection and has_confirmation
            })
    
    async def test_scenario_3_confirmation_flow(self, db):
        """Scenario 3: Confirmation flow (Yes/No)"""
        print("\n✅❌ Scenario 3: Confirmation flow")
        
        confirmation_tests = [
            # Yes responses
            {"message": "Yes", "expected_type": "accept"},
            {"message": "Có", "expected_type": "accept"},
            {"message": "Đồng ý", "expected_type": "accept"},
            {"message": "OK", "expected_type": "accept"},
            
            # No responses
            {"message": "No", "expected_type": "reject"},
            {"message": "Không", "expected_type": "reject"},
            {"message": "Không đồng ý", "expected_type": "reject"},
            {"message": "Cancel", "expected_type": "reject"}
        ]
        
        for i, test in enumerate(confirmation_tests):
            message = test["message"]
            expected_type = test["expected_type"]
            
            print(f"   Test {i+1}: '{message}' (Expected: {expected_type})")
            
            # Generate response
            response = await booking_response_generator.process_booking_request(
                user_message=message,
                conversation_history="",
                db_session=db
            )
            
            intent = response.get("intent", "")
            is_confirmation = intent == "A"
            is_acceptance = response.get("is_confirmation", False)
            is_rejection = response.get("is_rejection", False)
            
            actual_type = "accept" if is_acceptance else "reject" if is_rejection else "unknown"
            
            print(f"     Intent: {intent}, Confirmation: {is_confirmation}, Type: {actual_type}")
            
            # Store result
            self.test_results.append({
                "scenario": "Confirmation Flow",
                "test": i+1,
                "message": message,
                "intent": intent,
                "is_confirmation": is_confirmation,
                "actual_type": actual_type,
                "expected_type": expected_type,
                "passed": is_confirmation and actual_type == expected_type
            })
    
    async def test_scenario_4_continue_after_rejection(self, db):
        """Scenario 4: Continue conversation after rejection"""
        print("\n🔄 Scenario 4: Continue after rejection")
        
        continue_messages = [
            "Can you help me with something else?",
            "I have another question",
            "What other services do you offer?",
            "Tôi có câu hỏi khác",
            "Can I get information about universities?"
        ]
        
        for i, message in enumerate(continue_messages):
            print(f"   Test {i+1}: '{message}'")
            
            # Generate response
            response = await booking_response_generator.process_booking_request(
                user_message=message,
                conversation_history="",
                db_session=db
            )
            
            intent = response.get("intent", "")
            is_normal = intent not in ["A", "B", "C"]
            response_generated = bool(response)
            
            print(f"     Intent: {intent}, Normal conversation: {is_normal}, Response: {response_generated}")
            
            # Store result
            self.test_results.append({
                "scenario": "Continue After Rejection",
                "test": i+1,
                "message": message,
                "intent": intent,
                "is_normal": is_normal,
                "response_generated": response_generated,
                "expected": True,
                "passed": response_generated
            })
    
    async def test_scenario_5_edge_cases(self, db):
        """Scenario 5: Edge cases and error handling"""
        print("\n🔍 Scenario 5: Edge cases")
        
        edge_cases = [
            {"message": "", "description": "Empty message"},
            {"message": "   ", "description": "Whitespace only"},
            {"message": "😊😊😊", "description": "Only emojis"},
            {"message": "A" * 1001, "description": "Too long message"},
            {"message": "Book at 25:00", "description": "Invalid time"},
            {"message": "Book at 9:99", "description": "Invalid time format"},
            {"message": "Yes but maybe no", "description": "Ambiguous"},
            {"message": "I want to book but I'm not sure", "description": "Uncertain"}
        ]
        
        for i, case in enumerate(edge_cases):
            message = case["message"]
            description = case["description"]
            
            print(f"   Test {i+1}: {description}")
            
            try:
                # Generate response
                response = await booking_response_generator.process_booking_request(
                    user_message=message,
                    conversation_history="",
                    db_session=db
                )
                
                intent = response.get("intent", "")
                safety_score = response.get("safety_score", 0)
                response_generated = bool(response)
                
                print(f"     Intent: {intent}, Safety: {safety_score}, Response: {response_generated}")
                
                # Store result
                self.test_results.append({
                    "scenario": "Edge Cases",
                    "test": i+1,
                    "description": description,
                    "message": message[:20] + "..." if len(message) > 20 else message,
                    "intent": intent,
                    "safety_score": safety_score,
                    "response_generated": response_generated,
                    "expected": True,
                    "passed": True  # No exception thrown
                })
                
            except Exception as e:
                print(f"     Error: {str(e)}")
                self.test_results.append({
                    "scenario": "Edge Cases",
                    "test": i+1,
                    "description": description,
                    "message": message[:20] + "..." if len(message) > 20 else message,
                    "intent": "ERROR",
                    "error": str(e),
                    "expected": True,
                    "passed": False
                })
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 BOOKING SCENARIOS TEST SUMMARY")
        print("="*60)
        
        # Group results by scenario
        scenarios = {}
        for result in self.test_results:
            scenario = result["scenario"]
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(result)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.get("passed", False))
        
        print(f"\n📈 Overall Results:")
        print(f"   Total tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success rate: {(passed_tests/total_tests*100):.1f}%")
        
        print(f"\n📋 Results by Scenario:")
        for scenario, results in scenarios.items():
            passed = sum(1 for r in results if r.get("passed", False))
            total = len(results)
            print(f"   {scenario}: {passed}/{total} passed ({(passed/total*100):.1f}%)")
        
        print(f"\n❌ Failed Tests:")
        failed_tests = [r for r in self.test_results if not r.get("passed", False)]
        for test in failed_tests:
            scenario = test.get("scenario", "Unknown")
            test_num = test.get("test", "?")
            message = test.get("message", "No message")
            print(f"   - {scenario} Test {test_num}: '{message}'")
        
        if not failed_tests:
            print("   🎉 All tests passed!")
        
        print("\n" + "="*60)

async def main():
    """Main test function"""
    print("🚀 Starting Booking Scenarios Test")
    print("="*60)
    
    # Initialize test
    test = BookingScenariosTest()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Run all scenarios
        await test.test_scenario_1_normal_to_booking(db)
        await test.test_scenario_2_time_selection(db)
        await test.test_scenario_3_confirmation_flow(db)
        await test.test_scenario_4_continue_after_rejection(db)
        await test.test_scenario_5_edge_cases(db)
        
        # Print summary
        test.print_summary()
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Cuối file, bỏ dòng db.close() nếu có

if __name__ == "__main__":
    asyncio.run(main()) 