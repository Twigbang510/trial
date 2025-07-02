# 🛡️ **Unified Content Moderation System**
# Supports multiple approaches: OpenAI, Gemini, Local Models

# COMMENTED OUT - OpenAI Moderation (can be restored)
# from openai import OpenAI

# NEW: Multiple moderation approaches
import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.core.config import settings
import logging
import os
import asyncio
import time
from app.core.moderation_local import  ModerationResult as LocalModerationResult
import traceback

logger = logging.getLogger(__name__)

# COMMENTED OUT - OpenAI client configuration
# Configure OpenAI client
# client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None

# NEW: Configure Gemini for moderation
model = None
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        model = None

# NEW: Import local models if available
try:
    from app.core.moderation_local import moderate_content_local, moderate_content_ensemble
    LOCAL_MODELS_AVAILABLE = True
except ImportError:
    LOCAL_MODELS_AVAILABLE = False
    logger.warning("Local models not available. Install dependencies: pip install torch transformers")

class ModerationResult:
    def __init__(self, flagged: bool, harmful_score: float, categories: Dict[str, bool], category_scores: Dict[str, float]):
        self.flagged = flagged
        self.harmful_score = harmful_score
        self.categories = categories
        self.category_scores = category_scores
        
    @property
    def should_block(self) -> bool:
        """Check if content should be blocked (both flagged AND high harmful score)"""
        return self.flagged and self.harmful_score > settings.MODERATION_HARMFUL_THRESHOLD
    
    @property
    def should_warn(self) -> bool:
        """Check if content should trigger a warning (flagged OR high harmful score, but not both)"""
        return (self.flagged or self.harmful_score > settings.MODERATION_HARMFUL_THRESHOLD) and not self.should_block
    
    @property
    def violation_type(self) -> str:
        """Get the type of violation for logging"""
        if self.should_block:
            return "BLOCK"
        elif self.should_warn:
            return "WARNING"
        return "CLEAN"

def _convert_to_test_format(result: ModerationResult, method_used: str, detected_language: Optional[str] = None) -> Dict[str, Any]:
    """Convert ModerationResult to test-compatible dictionary format"""
    return {
        "is_safe": not result.flagged,  # Invert: flagged=True means toxic, is_safe=False means toxic
        "confidence": result.harmful_score,
        "language": detected_language or "unknown",
        "method": method_used,
        "flagged": result.flagged,
        "categories": result.categories,
        "category_scores": result.category_scores,
        "violation_type": result.violation_type
    }

async def moderate_content(text: str, language: Optional[str] = None) -> Dict[str, Any]:
    """
    Main content moderation function with multiple approaches
    
    Approach selection order:
    1. MODERATION_METHOD environment variable
    2. AUTO: Local -> Gemini -> OpenAI (fallback)
    
    Args:
        text: The text content to moderate
        language: Optional language code (e.g., 'en', 'vi') for language-specific processing
        
    Returns:
        Dict: Dictionary containing moderation results in test-compatible format
    """
    try:
        # Get moderation method preference
        moderation_method = os.getenv("MODERATION_METHOD", "auto").lower()
        
        logger.info(f"Moderating content with method: {moderation_method}")
        
        if moderation_method == "local" or moderation_method == "auto":
            # Try local models first
            if LOCAL_MODELS_AVAILABLE:
                try:
                    result = await moderate_content_local(text, model_preference="auto", language=language)
                    logger.info(f"Local moderation successful - Type: {result.violation_type}")
                    return _convert_to_test_format(result, "local", language)
                except Exception as e:
                    logger.warning(f"Local moderation failed: {str(e)}")
                    if moderation_method == "local":
                        # If specifically requested local but failed, return error result
                        error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
                        return _convert_to_test_format(error_result, "local", language)
            else:
                logger.warning("Local models not available, falling back to cloud services")
        
        if moderation_method == "ensemble" and LOCAL_MODELS_AVAILABLE:
            # Use ensemble of local models
            try:
                result = await moderate_content_ensemble(text)
                logger.info(f"Ensemble moderation successful - Type: {result.violation_type}")
                return _convert_to_test_format(result, "ensemble", language)
            except Exception as e:
                logger.warning(f"Ensemble moderation failed: {str(e)}")
        
        if moderation_method == "gemini" or moderation_method == "auto":
            # Try Gemini moderation
            if model and settings.GEMINI_API_KEY:
                try:
                    result = await _moderate_with_gemini(text)
                    logger.info(f"Gemini moderation successful - Type: {result.violation_type}")
                    return _convert_to_test_format(result, "gemini", language)
                except Exception as e:
                    logger.warning(f"Gemini moderation failed: {str(e)}")
                    if moderation_method == "gemini":
                        # If specifically requested Gemini but failed, return error result
                        error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
                        return _convert_to_test_format(error_result, "gemini", language)
            else:
                logger.warning("Gemini API key not configured")
        
        if moderation_method == "openai":
            # Use OpenAI moderation (from commented code)
            try:
                result = await _moderate_with_openai(text)
                logger.info(f"OpenAI moderation successful - Type: {result.violation_type}")
                return _convert_to_test_format(result, "openai", language)
            except Exception as e:
                logger.warning(f"OpenAI moderation failed: {str(e)}")
                error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
                return _convert_to_test_format(error_result, "openai", language)
        
        # Final fallback: keyword-based moderation
        logger.warning("All advanced moderation methods failed, using keyword fallback")
        result = await _moderate_with_keywords(text)
        return _convert_to_test_format(result, "keywords", language)
            
    except Exception as e:
        logger.error(f"Error in content moderation: {str(e)}")
        # In case of API failure, allow content but log the error
        error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        return _convert_to_test_format(error_result, "error", language)

async def _moderate_with_gemini(text: str) -> ModerationResult:
    """
    Moderate content using Gemini AI
    """
    try:
        moderation_prompt = f"""
You are a content moderation system. Analyze this text for harmful content and respond with a JSON object containing:
- "flagged": boolean (true if content is harmful)
- "harmful_score": float between 0.0-1.0 (higher = more harmful)
- "categories": object with boolean values for: hate, harassment, self-harm, sexual, violence, dangerous
- "category_scores": object with float scores 0.0-1.0 for each category

Text to analyze: "{text}"

Respond ONLY with valid JSON, no other text.
"""
        
        response = model.generate_content(moderation_prompt)
        
        # Parse JSON response (handle markdown code blocks)
        import json
        import re
        try:
            # Extract JSON from markdown code blocks if present
            response_text = response.text.strip()
            
            # Remove markdown code block wrapper if present
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
            else:
                json_text = response_text
            
            result_data = json.loads(json_text)
        except Exception as e:
            # Fallback if JSON parsing fails
            logger.warning(f"Failed to parse Gemini moderation response: {response.text}")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        # Extract data
        flagged = result_data.get('flagged', False)
        harmful_score = float(result_data.get('harmful_score', 0.0))
        categories = result_data.get('categories', {})
        category_scores = result_data.get('category_scores', {})
        
        moderation_result = ModerationResult(
            flagged=flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        
        # Log moderation result
        logger.info(f"Gemini Moderation result - Type: {moderation_result.violation_type}, "
                   f"Flagged: {flagged}, Harmful Score: {harmful_score:.3f}")
        
        if moderation_result.violation_type != "CLEAN":
            logger.warning(f"Content violation detected: {text[:100]}... - Categories: {categories}")
        
        return moderation_result
        
    except Exception as e:
        logger.error(f"Error in Gemini moderation: {str(e)}")
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})

async def _moderate_with_openai(text: str) -> ModerationResult:
    """
    Moderate content using OpenAI (restored from commented code)
    """
    try:
        # Import OpenAI here to avoid errors if not installed
        from openai import OpenAI
        
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        # Create clean OpenAI client without global configurations
        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,  # Set explicit timeout
        )
        
        # Call OpenAI Moderation API
        response = client.moderations.create(input=text)
        
        result = response.results[0]
        
        # Calculate overall harmful score (max of all category scores)
        harmful_score = max(result.category_scores.__dict__.values()) if result.category_scores else 0.0
        
        # Convert categories and category_scores to dict
        categories = result.categories.__dict__
        category_scores = result.category_scores.__dict__
        
        moderation_result = ModerationResult(
            flagged=result.flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        
        # Log moderation result
        logger.info(f"OpenAI Moderation result - Type: {moderation_result.violation_type}, "
                   f"Flagged: {result.flagged}, Harmful Score: {harmful_score:.3f}")
        
        if moderation_result.violation_type != "CLEAN":
            logger.warning(f"Content violation detected: {text[:100]}... - Categories: {categories}")
        
        return moderation_result
        
    except Exception as e:
        logger.error(f"Error in OpenAI moderation: {str(e)}")
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})

async def _moderate_with_keywords(text: str) -> ModerationResult:
    """
    Fallback keyword-based moderation
    """
    try:
        keyword_patterns = {
            'hate': ['hate', 'nazi', 'terrorist', 'kill', 'murder', 'death', 'violence'],
            'harassment': ['stupid', 'idiot', 'moron', 'ugly', 'fat', 'loser', 'freak'],
            'sexual': ['sex', 'porn', 'nude', 'naked', 'breast', 'penis', 'vagina'],
            'violence': ['violence', 'attack', 'bomb', 'weapon', 'fight', 'war', 'blood'],
            'vietnamese_hate': [
                'chết', 'giết', 'đánh', 'thù', 'ghét', 'ngu', 'đần', 'óc chó', 
                'súc vật', 'con lợn', 'đồ chó', 'thằng ngu', 'con khốn', 'đồ khốn'
            ]
        }
        
        text_lower = text.lower()
        categories = {}
        category_scores = {}
        max_score = 0.0
        
        for category, keywords in keyword_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            score = min(matches * 0.3, 1.0)
            categories[category] = score > 0.5
            category_scores[category] = score
            max_score = max(max_score, score)
        
        return ModerationResult(
            flagged=max_score > 0.5,
            harmful_score=max_score,
            categories=categories,
            category_scores=category_scores
        )
        
    except Exception as e:
        logger.error(f"Error in keyword moderation: {str(e)}")
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})

# ========================================
# ORIGINAL OPENAI CODE
# ========================================
"""
async def moderate_content(text: str) -> ModerationResult:
    \"\"\"
    Moderate content using OpenAI's Moderation API
    
    Args:
        text: The text content to moderate
        
    Returns:
        ModerationResult: Object containing moderation results
        
    Raises:
        Exception: If moderation API call fails
    \"\"\"
    try:
        if not client or not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured, skipping moderation")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        # Call OpenAI Moderation API
        response = client.moderations.create(input=text)
        
        result = response.results[0]
        
        # Calculate overall harmful score (max of all category scores)
        harmful_score = max(result.category_scores.__dict__.values()) if result.category_scores else 0.0
        
        # Convert categories and category_scores to dict
        categories = result.categories.__dict__
        category_scores = result.category_scores.__dict__
        
        moderation_result = ModerationResult(
            flagged=result.flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        
        # Log moderation result
        logger.info(f"Moderation result - Type: {moderation_result.violation_type}, "
                   f"Flagged: {result.flagged}, Harmful Score: {harmful_score:.3f}")
        
        if moderation_result.violation_type != "CLEAN":
            logger.warning(f"Content violation detected: {text[:100]}... - Categories: {categories}")
        
        return moderation_result
        
    except Exception as e:
        logger.error(f"Error in content moderation: {str(e)}")
        # In case of API failure, allow content but log the error
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={}) 
""" 