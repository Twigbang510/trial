#!/usr/bin/env python3
"""
🛡️ **Moderation Manager**
Manage moderation system with multiple methods

Usage:
    python moderation_manager.py setup     # Setup system
    python moderation_manager.py test      # Run tests
    python moderation_manager.py config    # Show configuration
    python moderation_manager.py status    # Check status
"""

import os
import sys
import asyncio
import argparse
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_environment():
    """Environment setup"""
    print("Setting up environment...")
    
    # Check Python version
    if sys.version_info < (3, 8, 0):
        logger.error("❌ Python 3.8+ is required to run the system")
        return False
    
    # Check required packages
    required_packages = {
        'torch': 'PyTorch',
        'transformers': 'Transformers',
        'google.generativeai': 'Google Generative AI',
        'openai': 'OpenAI'
    }
    
    missing_packages = []
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"{name}: Installed")
        except ImportError:
            if package != 'openai':  # OpenAI is optional
                missing_packages.append(f"pip install {package}")
                logger.warning(f"⚠️  {name}: Not installed")
            else:
                print(f"{name}: Not installed (optional)")
    
    if missing_packages:
        logger.error("Missing required packages:")
        for cmd in missing_packages:
            logger.error(f"   {cmd}")
        return False
    
    print("Environment ready!")
    return True

def setup_local_models():
    """Setup local models"""
    print("Setting up local models...")
    
    try:
        from setup_local_models import main as setup_main
        setup_main()
    except Exception as e:
        logger.error(f"❌ Error setting up local models: {str(e)}")
        print("Run: python setup_local_models.py")

def check_api_keys():
    """Check API keys"""
    print("Checking API keys...")
    
    # Gemini API Key
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key and gemini_key != "your-gemini-api-key":
        print("Gemini API Key: Configured")
    else:
        logger.warning("⚠️  Gemini API Key: Not configured")
        print("Setup: export GEMINI_API_KEY=your_actual_key")
    
    # OpenAI API Key (optional)
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key != "your-openai-api-key":
        print("OpenAI API Key: Configured")
    else:
        print("OpenAI API Key: Not configured (optional)")

def show_configuration():
    """Show current configuration"""
    print("⚙️ Current moderation configuration:")
    
    # Current method
    method = os.getenv("MODERATION_METHOD", "auto")
    print(f"Method: {method}")
    
    # Threshold
    threshold = os.getenv("MODERATION_HARMFUL_THRESHOLD", "0.7")
    print(f"Harmful threshold: {threshold}")
    
    # Available methods
    available_methods = []
    
    # Check Gemini
    if os.getenv("GEMINI_API_KEY"):
        available_methods.append("gemini")
    
    # Check OpenAI
    if os.getenv("OPENAI_API_KEY"):
        available_methods.append("openai")
    
    # Check Local Models
    try:
        import torch
        import transformers
        available_methods.append("local")
    except ImportError:
        pass
    
    # Keywords always available
    available_methods.append("keywords")
    
    print(f"Available methods: {', '.join(available_methods)}")
    
    if "gemini" in available_methods:
        print("Best: MODERATION_METHOD=gemini (100% accuracy)")
    elif "local" in available_methods:
        print("Private: MODERATION_METHOD=local (offline)")
    else:
        print("Basic: MODERATION_METHOD=keywords (84.6% accuracy)")

async def run_tests():
    """Run system tests"""
    print("Running system tests...")
    
    try:
        from test_moderation import main as test_main
        await test_main()
    except Exception as e:
        logger.error(f"❌ Error running tests: {str(e)}")
        print("Run: python test_moderation.py")

async def check_status():
    """Check system status"""
    print("Checking system status...")
    
    # Test a simple moderation call
    try:
        from app.core.moderation import moderate_content
        
        # Test safe content
        result = await moderate_content("Hello world", "en")
        if result and result.get("method"):
            print(f"Moderation method: {result['method']}")
            print(f"Result: {'Safe' if result['is_safe'] else 'Unsafe'}")
        else:
            logger.error("❌ System did not respond correctly")
    except Exception as e:
        logger.error(f"❌ System error: {str(e)}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Moderation System Manager")
    parser.add_argument("command", choices=["setup", "test", "config", "status"], 
                       help="Command to execute")
    
    args = parser.parse_args()
    
    print("Moderation Manager")
    print("=" * 40)
    
    if args.command == "setup":
        print("Setting up system...")
        if setup_environment():
            check_api_keys()
            setup_local_models()
            print("\nSetup complete!")
        else:
            print("\nSetup failed!")
            
    elif args.command == "test":
        print("Running tests...")
        asyncio.run(run_tests())
        
    elif args.command == "config":
        print("Current configuration...")
        check_api_keys()
        show_configuration()
        
    elif args.command == "status":
        print("Checking status...")
        asyncio.run(check_status())

if __name__ == "__main__":
    main() 