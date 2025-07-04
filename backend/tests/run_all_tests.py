#!/usr/bin/env python3
"""
Usage:
    python tests/run_all_tests.py              # Run all tests
    python tests/run_all_tests.py --api        # Run only API tests
    python tests/run_all_tests.py --booking    # Run only booking tests
    python tests/run_all_tests.py --integration # Run only integration tests
    python tests/run_all_tests.py --utils      # Run only utils tests
"""

import asyncio
import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import test modules
from tests.api.test_chatbot import TestChatbotAPI
from tests.booking.test_booking_system import run_booking_tests
from tests.integration.test_e2e_booking import run_integration_tests
from tests.utils.test_moderation import run_utils_tests

def run_api_tests():
    """Run API test suite"""
    print("🚀 Running API Tests...")
    try:
        api_tests = TestChatbotAPI()
        
        api_tests.test_chat_endpoint_exists()
        api_tests.test_chat_general_question()
        api_tests.test_chat_booking_question()
        api_tests.test_conversation_endpoints()
        api_tests.test_invalid_requests()
        
        print("✅ API tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ API tests failed: {e}")
        return False

async def run_all_test_suites():
    """Run all test suites"""
    print("🧪 TRIAL-WEBAPP BACKEND TEST SUITE")
    print("=" * 60)
    
    results = {
        "api": False,
        "booking": False,
        "integration": False,
        "utils": False
    }
    
    try:
        # Run API tests
        print("\n" + "=" * 20 + " API TESTS " + "=" * 20)
        results["api"] = run_api_tests()
        
        # Run booking tests
        print("\n" + "=" * 18 + " BOOKING TESTS " + "=" * 18)
        try:
            await run_booking_tests()
            results["booking"] = True
        except Exception as e:
            print(f"❌ Booking tests failed: {e}")
        
        # Run integration tests
        print("\n" + "=" * 16 + " INTEGRATION TESTS " + "=" * 16)
        try:
            run_integration_tests()
            results["integration"] = True
        except Exception as e:
            print(f"❌ Integration tests failed: {e}")
        
        # Run utils tests
        print("\n" + "=" * 19 + " UTILS TESTS " + "=" * 19)
        try:
            await run_utils_tests()
            results["utils"] = True
        except Exception as e:
            print(f"❌ Utils tests failed: {e}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_suites = len(results)
        passed_suites = sum(1 for result in results.values() if result)
        
        for suite, result in results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{suite.upper():15} : {status}")
        
        print(f"\nOVERALL: {passed_suites}/{total_suites} test suites passed")
        
        if passed_suites == total_suites:
            print("🎉 ALL TESTS PASSED! System is healthy.")
            return True
        else:
            print("⚠️  Some tests failed. Check logs above for details.")
            return False
            
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run trial-webapp backend tests")
    parser.add_argument("--api", action="store_true", help="Run only API tests")
    parser.add_argument("--booking", action="store_true", help="Run only booking tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--utils", action="store_true", help="Run only utils tests")
    
    args = parser.parse_args()
    
    # If no specific test suite selected, run all
    if not any([args.api, args.booking, args.integration, args.utils]):
        print("No specific test suite selected. Running all tests...")
        success = asyncio.run(run_all_test_suites())
        sys.exit(0 if success else 1)
    
    # Run specific test suites
    async def run_selected_tests():
        success = True
        
        if args.api:
            print("Running API tests...")
            if not run_api_tests():
                success = False
        
        if args.booking:
            print("Running booking tests...")
            try:
                await run_booking_tests()
            except Exception as e:
                print(f"❌ Booking tests failed: {e}")
                success = False
        
        if args.integration:
            print("Running integration tests...")
            try:
                run_integration_tests()
            except Exception as e:
                print(f"❌ Integration tests failed: {e}")
                success = False
        
        if args.utils:
            print("Running utils tests...")
            try:
                await run_utils_tests()
            except Exception as e:
                print(f"❌ Utils tests failed: {e}")
                success = False
        
        return success
    
    success = asyncio.run(run_selected_tests())
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 