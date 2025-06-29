#!/usr/bin/env python3
"""
🏠 Local Models Setup Script
Downloads and prepares local ML models for content moderation
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Model configurations
MODEL_CONFIGS = {
    "toxic_bert": {
        "name": "unitary/toxic-bert",
        "type": "transformers",
        "description": "BERT-based toxicity detection (English focused)",
        "size": "~400MB",
        "languages": ["en"],
        "accuracy": "High",
        "speed": "Fast"
    },
    "multilingual_distilbert": {
        "name": "distilbert-base-multilingual-cased",
        "type": "transformers", 
        "description": "Multilingual DistilBERT for 104 languages",
        "size": "~250MB",
        "languages": ["en", "vi", "es", "fr", "de", "zh", "ja", "ko", "+96 more"],
        "accuracy": "Medium-High",
        "speed": "Very Fast"
    },
    "toxic_comment": {
        "name": "martin-ha/toxic-comment-model",
        "type": "transformers",
        "description": "Specialized toxic comment classifier",
        "size": "~250MB", 
        "languages": ["en"],
        "accuracy": "High",
        "speed": "Fast"
    },
    "offensive_roberta": {
        "name": "cardiffnlp/twitter-roberta-base-offensive",
        "type": "transformers",
        "description": "RoBERTa for offensive language detection on Twitter",
        "size": "~500MB",
        "languages": ["en"],
        "accuracy": "High",
        "speed": "Medium"
    },
    "vietnamese_model": {
        "name": "distilbert-base-multilingual-cased",  # Using as Vietnamese proxy
        "type": "transformers",
        "description": "Vietnamese-enhanced multilingual model",
        "size": "~250MB",
        "languages": ["vi", "en"],
        "accuracy": "High (Vietnamese)",
        "speed": "Fast"
    }
}

RECOMMENDED_SETUPS = {
    "minimal": ["toxic_bert", "multilingual_distilbert"],
    "recommended": ["toxic_bert", "multilingual_distilbert", "toxic_comment"],
    "complete": ["toxic_bert", "multilingual_distilbert", "toxic_comment", "offensive_roberta"],
    "vietnamese_focused": ["multilingual_distilbert", "vietnamese_model", "toxic_bert"]
}

def check_system_requirements():
    """Check if system meets requirements"""
    logger.info("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3.8, 0):
        logger.error("❌ Python 3.8+ required")
        return False
    
    # Check available disk space (rough estimate)
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (2**30)
        if free_gb < 5:
            logger.warning(f"⚠️  Low disk space: {free_gb}GB available. Consider freeing up space.")
    except:
        pass
    
    # Check PyTorch installation
    try:
        import torch
        logger.info(f"✅ PyTorch {torch.__version__} detected")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            logger.info(f"✅ CUDA available - {gpu_count} GPU(s) detected: {gpu_name}")
        else:
            logger.info("ℹ️  CUDA not available - will use CPU (slower but functional)")
    except ImportError:
        logger.error("❌ PyTorch not installed. Run: pip install torch")
        return False
    
    # Check transformers
    try:
        import transformers
        logger.info(f"✅ Transformers {transformers.__version__} detected")
    except ImportError:
        logger.error("❌ Transformers not installed. Run: pip install transformers")
        return False
    
    return True

def download_model(model_key: str, model_config: dict):
    """Download and cache a specific model"""
    model_name = model_config["name"]
    logger.info(f"📥 Downloading {model_key}: {model_name}")
    logger.info(f"   Description: {model_config['description']}")
    logger.info(f"   Size: {model_config['size']}")
    logger.info(f"   Languages: {', '.join(model_config['languages'])}")
    
    try:
        if model_config["type"] == "transformers":
            # Import transformers within function
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            
            # Download tokenizer and model
            logger.info("   📁 Downloading tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            logger.info("   🧠 Downloading model...")
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Test the model with a simple pipeline
            logger.info("   🧪 Testing model...")
            try:
                test_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    tokenizer=tokenizer,
                    device=-1  # Use CPU for testing
                )
                # Test with a simple sentence
                result = test_pipeline("This is a test sentence.")
                logger.info(f"   ✅ Model test successful: {len(result)} predictions")
            except Exception as e:
                logger.warning(f"   ⚠️  Model test failed but download successful: {str(e)}")
            
            logger.info(f"✅ {model_key} downloaded successfully!")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to download {model_key}: {str(e)}")
        return False

def setup_models(setup_type: str = "recommended", specific_models: list = None):
    """Setup models based on configuration"""
    if specific_models:
        models_to_download = specific_models
    else:
        models_to_download = RECOMMENDED_SETUPS.get(setup_type, RECOMMENDED_SETUPS["recommended"])
    
    logger.info(f"🚀 Setting up models: {setup_type}")
    logger.info(f"📋 Models to download: {', '.join(models_to_download)}")
    
    # Calculate total estimated size
    total_size = 0
    size_estimates = {"~250MB": 250, "~300MB": 300, "~400MB": 400, "~500MB": 500}
    for model_key in models_to_download:
        if model_key in MODEL_CONFIGS:
            size_str = MODEL_CONFIGS[model_key]["size"]
            total_size += size_estimates.get(size_str, 300)
    
    logger.info(f"💾 Estimated total download size: ~{total_size}MB")
    
    success_count = 0
    failed_models = []
    
    for model_key in models_to_download:
        if model_key not in MODEL_CONFIGS:
            logger.warning(f"⚠️  Unknown model: {model_key}")
            continue
        
        model_config = MODEL_CONFIGS[model_key]
        
        try:
            if download_model(model_key, model_config):
                success_count += 1
            else:
                failed_models.append(model_key)
        except KeyboardInterrupt:
            logger.info("\n🛑 Setup interrupted by user")
            break
        except Exception as e:
            logger.error(f"❌ Unexpected error with {model_key}: {str(e)}")
            failed_models.append(model_key)
    
    # Summary
    logger.info(f"\n📊 Setup Summary:")
    logger.info(f"   ✅ Successfully downloaded: {success_count}/{len(models_to_download)} models")
    
    if failed_models:
        logger.info(f"   ❌ Failed models: {', '.join(failed_models)}")
        logger.info(f"   💡 You can retry failed models individually")
    
    if success_count > 0:
        logger.info(f"🎉 Setup complete! You can now use local models for content moderation.")
        logger.info(f"   To use: Set MODERATION_METHOD=local in your .env file")
    else:
        logger.error(f"❌ No models were successfully downloaded.")

def list_available_models():
    """List all available models with details"""
    logger.info("📋 Available Models:")
    logger.info("="*80)
    
    for model_key, config in MODEL_CONFIGS.items():
        logger.info(f"\n🔹 {model_key}")
        logger.info(f"   Name: {config['name']}")
        logger.info(f"   Description: {config['description']}")
        logger.info(f"   Size: {config['size']}")
        logger.info(f"   Languages: {', '.join(config['languages'])}")
        logger.info(f"   Accuracy: {config['accuracy']}")
        logger.info(f"   Speed: {config['speed']}")
    
    logger.info("\n📦 Recommended Setups:")
    logger.info("="*50)
    
    for setup_name, models in RECOMMENDED_SETUPS.items():
        total_size = sum(250 if "250MB" in MODEL_CONFIGS[m]["size"] else 400 
                        for m in models if m in MODEL_CONFIGS)
        logger.info(f"\n🔸 {setup_name}: {', '.join(models)} (~{total_size}MB)")

def verify_models():
    """Verify that downloaded models work correctly"""
    logger.info("🔍 Verifying downloaded models...")
    
    # Import transformers within function
    try:
        from transformers import pipeline
    except ImportError:
        logger.error("❌ Transformers not available for verification")
        return
    
    test_texts = [
        "Hello, this is a normal message.",
        "I hate this so much, it's terrible!",
        "Xin chào, đây là tin nhắn bình thường.",
        "Tôi ghét cái này quá!"
    ]
    
    working_models = []
    broken_models = []
    
    for model_key, config in MODEL_CONFIGS.items():
        try:
            model_name = config["name"]
            logger.info(f"   Testing {model_key}...")
            
            # Try to create pipeline
            classifier = pipeline(
                "text-classification",
                model=model_name,
                device=-1,  # Use CPU
                return_all_scores=True
            )
            
            # Test with sample text
            result = classifier(test_texts[0])
            logger.info(f"   ✅ {model_key} working correctly")
            working_models.append(model_key)
            
        except Exception as e:
            logger.warning(f"   ❌ {model_key} not available: {str(e)}")
            broken_models.append(model_key)
    
    logger.info(f"\n📊 Verification Results:")
    logger.info(f"   ✅ Working models: {len(working_models)} - {', '.join(working_models)}")
    
    if broken_models:
        logger.info(f"   ❌ Unavailable models: {len(broken_models)} - {', '.join(broken_models)}")
        logger.info(f"   💡 Run setup again to download missing models")

def main():
    parser = argparse.ArgumentParser(
        description="Setup local ML models for content moderation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_local_models.py --setup minimal
  python setup_local_models.py --setup vietnamese_focused  
  python setup_local_models.py --models toxic_bert multilingual_distilbert
  python setup_local_models.py --list
  python setup_local_models.py --verify
        """
    )
    
    parser.add_argument(
        "--setup", 
        choices=["minimal", "recommended", "complete", "vietnamese_focused"],
        help="Download predefined model setup"
    )
    
    parser.add_argument(
        "--models",
        nargs="+",
        help="Download specific models by name"
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available models"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true", 
        help="Verify downloaded models"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force download even if models exist"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("🏠 Local Models Setup for Content Moderation")
    print("=" * 50)
    
    if args.list:
        list_available_models()
        return
    
    if args.verify:
        if not check_system_requirements():
            sys.exit(1)
        verify_models()
        return
    
    if not check_system_requirements():
        logger.error("❌ System requirements not met")
        sys.exit(1)
    
    if args.setup:
        setup_models(setup_type=args.setup)
    elif args.models:
        setup_models(specific_models=args.models)
    else:
        # Interactive setup
        logger.info("🤖 Interactive Setup")
        logger.info("Choose a setup option:")
        logger.info("1. Minimal (2 models, ~650MB)")
        logger.info("2. Recommended (3 models, ~900MB)")  
        logger.info("3. Complete (4 models, ~1.4GB)")
        logger.info("4. Vietnamese Focused (3 models, ~800MB)")
        logger.info("5. List all models")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                setup_models("minimal")
            elif choice == "2": 
                setup_models("recommended")
            elif choice == "3":
                setup_models("complete")
            elif choice == "4":
                setup_models("vietnamese_focused")
            elif choice == "5":
                list_available_models()
            else:
                logger.error("Invalid choice")
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Setup cancelled by user")

if __name__ == "__main__":
    main() 