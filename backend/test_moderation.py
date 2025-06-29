#!/usr/bin/env python3
"""
🧪 Moderation System Test Script
Tests all moderation methods without downloading models
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.moderation import moderate_content
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Test cases in multiple languages
TEST_CASES = [
    # English tests
    {"text": "Hello, this is a nice message!", "language": "en", "expected": "safe"},
    {"text": "I hate you so much, you idiot!", "language": "en", "expected": "toxic"},
    {"text": "This product is terrible and waste of money", "language": "en", "expected": "safe"},
    {"text": "You are stupid and deserve to die", "language": "en", "expected": "toxic"},
    
    # Vietnamese tests  
    {"text": "Xin chào, tôi rất vui được gặp bạn!", "language": "vi", "expected": "safe"},
    {"text": "Tôi ghét bạn, bạn thật là ngu ngốc!", "language": "vi", "expected": "toxic"},
    {"text": "Sản phẩm này không tốt lắm", "language": "vi", "expected": "safe"},
    {"text": "Mày là đồ khốn nạn, chết đi!", "language": "vi", "expected": "toxic"},
    
    # Mixed content
    {"text": "This is a normal message with some 🙂 emojis", "language": "en", "expected": "safe"},
    {"text": "Email: test@example.com and phone: 123-456-7890", "language": "en", "expected": "safe"},
    
    # Edge cases
    {"text": "", "language": "en", "expected": "safe"},
    {"text": "a", "language": "en", "expected": "safe"},
    {"text": "   ", "language": "en", "expected": "safe"},
]

async def test_moderation_method(method_name: str, test_cases: list):
    """Test a specific moderation method"""
    logger.info(f"\n🔍 Testing {method_name.upper()} moderation...")
    
    # Set environment variable for testing
    original_method = os.environ.get('MODERATION_METHOD')
    os.environ['MODERATION_METHOD'] = method_name
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        text = test_case["text"]
        language = test_case["language"]
        expected = test_case["expected"]
        
        try:
            # Test the moderation
            result = await moderate_content(text, language)
            
            # Check result
            is_safe = result.get("is_safe", True)
            confidence = result.get("confidence", 0.0)
            detected_language = result.get("language", "unknown")
            method_used = result.get("method", "unknown")
            
            # Determine if test passed
            actual = "safe" if is_safe else "toxic"
            test_passed = actual == expected
            
            if test_passed:
                passed_tests += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
            
            # Log result
            text_preview = text[:50] + "..." if len(text) > 50 else text
            logger.info(f"   {i:2d}/{total_tests} {status} [{language}] \"{text_preview}\"")
            logger.info(f"        Expected: {expected}, Got: {actual}, Confidence: {confidence:.2f}, Method: {method_used}")
            
            results.append({
                "text": text,
                "language": language,
                "expected": expected,
                "actual": actual,
                "confidence": confidence,
                "method_used": method_used,
                "passed": test_passed
            })
            
        except Exception as e:
            logger.error(f"   {i:2d}/{total_tests} ❌ ERROR [{language}] \"{text[:30]}...\": {str(e)}")
            results.append({
                "text": text,
                "language": language,
                "expected": expected,
                "actual": "error",
                "confidence": 0.0,
                "method_used": "error",
                "passed": False,
                "error": str(e)
            })
    
    # Restore original environment
    if original_method:
        os.environ['MODERATION_METHOD'] = original_method
    else:
        os.environ.pop('MODERATION_METHOD', None)
    
    # Calculate accuracy
    accuracy = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    logger.info(f"\n📊 {method_name.upper()} Results:")
    logger.info(f"   ✅ Passed: {passed_tests}/{total_tests} ({accuracy:.1f}%)")
    logger.info(f"   ❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    return results, accuracy

async def test_all_methods():
    """Test all available moderation methods"""
    logger.info("🚀 Starting Moderation System Tests")
    logger.info("=" * 60)
    
    # Test methods in order of preference
    methods_to_test = [
        "keywords",  # Always available
        "gemini",    # If API key available
        "openai",    # If API key available  
        "local",     # If models available
        "auto"       # Auto-selection
    ]
    
    all_results = {}
    
    for method in methods_to_test:
        try:
            results, accuracy = await test_moderation_method(method, TEST_CASES)
            all_results[method] = {
                "results": results,
                "accuracy": accuracy
            }
        except Exception as e:
            logger.error(f"❌ Failed to test {method}: {str(e)}")
            all_results[method] = {
                "results": [],
                "accuracy": 0,
                "error": str(e)
            }
    
    # Summary
    logger.info("\n📋 FINAL SUMMARY")
    logger.info("=" * 60)
    
    for method, data in all_results.items():
        if "error" in data:
            logger.info(f"   {method.upper():8} - ❌ Error: {data['error']}")
        else:
            accuracy = data["accuracy"]
            status = "✅" if accuracy >= 70 else "⚠️" if accuracy >= 50 else "❌"
            logger.info(f"   {method.upper():8} - {status} {accuracy:.1f}% accuracy")
    
    # Recommendations
    logger.info("\n💡 RECOMMENDATIONS")
    logger.info("=" * 30)
    
    working_methods = [(method, data["accuracy"]) for method, data in all_results.items() 
                      if "error" not in data and data["accuracy"] > 0]
    
    if working_methods:
        # Sort by accuracy
        working_methods.sort(key=lambda x: x[1], reverse=True)
        best_method, best_accuracy = working_methods[0]
        
        logger.info(f"🏆 Best performing method: {best_method.upper()} ({best_accuracy:.1f}%)")
        logger.info(f"🔧 To use: Set MODERATION_METHOD={best_method} in .env")
        
        if best_method == "keywords" and len(working_methods) == 1:
            logger.info("⚠️  Only keyword-based moderation is working")
            logger.info("💡 Consider setting up Gemini API or local models for better accuracy")
        
    else:
        logger.error("❌ No moderation methods are working!")
        logger.info("🔧 Please check your API keys and dependencies")

def check_api_keys():
    """Check which API keys are available"""
    logger.info("🔑 Checking API Keys...")
    
    gemini_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    openai_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    
    if gemini_key and gemini_key != "your-gemini-api-key":
        logger.info("   ✅ Gemini API key found")
    else:
        logger.info("   ❌ Gemini API key not configured")
    
    if openai_key and openai_key != "your-openai-api-key":
        logger.info("   ✅ OpenAI API key found")
    else:
        logger.info("   ❌ OpenAI API key not configured")

def check_local_models():
    """Check if local models are available"""
    logger.info("🤖 Checking Local Models...")
    
    try:
        import torch
        import transformers
        logger.info("   ✅ PyTorch and Transformers available")
        
        # Try to load a simple model to test
        try:
            from transformers import pipeline
            # Try to create a very basic pipeline
            classifier = pipeline("sentiment-analysis", 
                                model="distilbert-base-uncased-finetuned-sst-2-english",
                                device=-1)  # CPU
            result = classifier("test")
            logger.info("   ✅ Local models can be loaded")
        except Exception as e:
            logger.info(f"   ⚠️  Local models not ready: {str(e)}")
    except ImportError as e:
        logger.info(f"   ❌ ML dependencies missing: {str(e)}")

async def main():
    """Main test function"""
    print("🧪 Moderation System Test Suite")
    print("=" * 50)
    
    # Pre-flight checks
    check_api_keys()
    check_local_models()
    
    # Run comprehensive tests
    await test_all_methods()
    
    print("\n✨ Testing complete!")
    print("📚 Check the logs above for detailed results and recommendations.")

if __name__ == "__main__":
    asyncio.run(main()) 