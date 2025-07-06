import google.generativeai as genai
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.core.prompts import moderation_prompt
import logging
import os
import asyncio
import time
from app.core.moderation_local import  ModerationResult as LocalModerationResult
import traceback

logger = logging.getLogger(__name__)

model = None
if settings.GEMINI_API_KEY:
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
    except Exception as e:
        logger.error(f"Failed to initialize Gemini: {e}")
        model = None

try:
    from app.core.moderation_local import moderate_content_local, moderate_content_ensemble
    LOCAL_MODELS_AVAILABLE = True
except ImportError:
    LOCAL_MODELS_AVAILABLE = False
    logger.warning("Local models not available. Install dependencies: pip install torch transformers")

class ModerationResult:
    """Result object for content moderation"""
    def __init__(self, flagged: bool, harmful_score: float, categories: Dict[str, bool], category_scores: Dict[str, float]):
        self.flagged = flagged
        self.harmful_score = harmful_score
        self.categories = categories
        self.category_scores = category_scores
        
    @property
    def should_block(self) -> bool:
        return self.flagged and self.harmful_score > settings.MODERATION_HARMFUL_THRESHOLD
    
    @property
    def should_warn(self) -> bool:
        return (self.flagged or self.harmful_score > settings.MODERATION_HARMFUL_THRESHOLD) and not self.should_block
    
    @property
    def violation_type(self) -> str:
        if self.should_block:
            return "BLOCK"
        elif self.should_warn:
            return "WARNING"
        return "CLEAN"

def _convert_to_test_format(result: ModerationResult, method_used: str, detected_language: Optional[str] = None) -> Dict[str, Any]:
    """Convert ModerationResult to test-compatible dictionary format"""
    return {
        "is_safe": not result.flagged,
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
        moderation_method = os.getenv("MODERATION_METHOD", "gemini").lower()
        
        print(f"Moderating content with method: {moderation_method}")
        
        if moderation_method == "local" or moderation_method == "auto":
            if LOCAL_MODELS_AVAILABLE:
                try:
                    result = await moderate_content_local(text, model_preference="auto", language=language)
                    print(f"Local moderation successful - Type: {result.violation_type}")
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
            try:
                result = await moderate_content_ensemble(text)
                print(f"Ensemble moderation successful - Type: {result.violation_type}")
                return _convert_to_test_format(result, "ensemble", language)
            except Exception as e:
                logger.warning(f"Ensemble moderation failed: {str(e)}")
        
        if moderation_method == "gemini" or moderation_method == "auto":
            if model and settings.GEMINI_API_KEY:
                try:
                    result = await _moderate_with_gemini(text)
                    print(f"Gemini moderation successful - Type: {result.violation_type}")
                    return _convert_to_test_format(result, "gemini", language)
                except Exception as e:
                    logger.warning(f"Gemini moderation failed: {str(e)}")
                    if moderation_method == "gemini":
                        error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
                        return _convert_to_test_format(error_result, "gemini", language)
            else:
                logger.warning("Gemini API key not configured")
        
        if moderation_method == "openai":
            try:
                result = await _moderate_with_openai(text)
                print(f"OpenAI moderation successful - Type: {result.violation_type}")
                return _convert_to_test_format(result, "openai", language)
            except Exception as e:
                logger.warning(f"OpenAI moderation failed: {str(e)}")
                error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
                return _convert_to_test_format(error_result, "openai", language)
        
        logger.warning("All advanced moderation methods failed, using keyword fallback")
        result = await _moderate_with_keywords(text)
        return _convert_to_test_format(result, "keywords", language)
            
    except Exception as e:
        logger.error(f"Error in content moderation: {str(e)}")
        error_result = ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        return _convert_to_test_format(error_result, "error", language)

async def _moderate_with_gemini(text: str) -> ModerationResult:
    """
    Moderate content using Gemini AI
    """
    try:
        full_prompt = f"""
{moderation_prompt}

## Text to Analyze:
"{text}"

Please analyze this content and respond with a JSON object containing:
- "flagged": boolean (true if content is harmful)
- "harmful_score": integer between 0-100 (higher = more harmful)
- "violation_type": string ("none", "inappropriate", "spam", "harassment", "other")
- "reasoning": string (explanation for your decision)

Respond ONLY with valid JSON, no other text.
"""
        
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=500,
            )
        )
        
        import json
        import re
        try:
            response_text = response.text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                function_result = json.loads(json_text)
            else:
                function_result = {}
        except Exception as e:
            print(f"Failed to parse moderation response: {e}")
            function_result = {}
        
        flagged = function_result.get('flagged', False)
        harmful_score = float(function_result.get('harmful_score', 0)) / 100.0  # Convert 0-100 to 0.0-1.0
        violation_type = function_result.get('violation_type', 'none')
        
        categories = {
            'hate': violation_type == 'inappropriate',
            'harassment': violation_type == 'harassment',
            'self-harm': False,
            'sexual': violation_type == 'inappropriate',
            'violence': violation_type == 'harassment',
            'dangerous': violation_type == 'other'
        }
        
        category_scores = {
            'hate': harmful_score if violation_type == 'inappropriate' else 0.0,
            'harassment': harmful_score if violation_type == 'harassment' else 0.0,
            'self-harm': 0.0,
            'sexual': harmful_score if violation_type == 'inappropriate' else 0.0,
            'violence': harmful_score if violation_type == 'harassment' else 0.0,
            'dangerous': harmful_score if violation_type == 'other' else 0.0
        }
        
        moderation_result = ModerationResult(
            flagged=flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        

        print(f"Gemini Moderation result - Type: {moderation_result.violation_type}, "
                   f"Flagged: {flagged}, Harmful Score: {harmful_score:.3f}")
        
        if moderation_result.violation_type != "CLEAN":
            logger.warning(f"Content violation detected: {text[:100]}... - Categories: {categories}")
        
        return moderation_result
        
    except Exception as e:
        logger.error(f"Error in Gemini moderation: {str(e)}")
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})

def _extract_moderation_function_result(response) -> Dict:
    """Extract function call result from moderation response (legacy method - not used)"""
    try:
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    return part.function_call.args
        return {}
    except Exception as e:
        logger.warning(f"Moderation function call extraction failed: {e}")
        return {}

async def _moderate_with_openai(text: str) -> ModerationResult:
    """
    Moderate content using OpenAI (enhanced method)
    """
    try:
        from openai import OpenAI
        
        if not settings.OPENAI_API_KEY:
            logger.warning("OpenAI API key not configured")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})

        client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=30.0,
        )
        
        response = client.moderations.create(input=text)
        
        result = response.results[0]
        
        harmful_score = max(result.category_scores.__dict__.values()) if result.category_scores else 0.0
        
        categories = result.categories.__dict__
        category_scores = result.category_scores.__dict__
        
        moderation_result = ModerationResult(
            flagged=result.flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        
        print(f"OpenAI Moderation result - Type: {moderation_result.violation_type}, "
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
        
        response = client.moderations.create(input=text)
        
        result = response.results[0]
        
        harmful_score = max(result.category_scores.__dict__.values()) if result.category_scores else 0.0
        
        categories = result.categories.__dict__
        category_scores = result.category_scores.__dict__
        
        moderation_result = ModerationResult(
            flagged=result.flagged,
            harmful_score=harmful_score,
            categories=categories,
            category_scores=category_scores
        )
        
        print(f"Moderation result - Type: {moderation_result.violation_type}, "
                   f"Flagged: {result.flagged}, Harmful Score: {harmful_score:.3f}")
        
        if moderation_result.violation_type != "CLEAN":
            logger.warning(f"Content violation detected: {text[:100]}... - Categories: {categories}")
        
        return moderation_result
        
    except Exception as e:
        logger.error(f"Error in content moderation: {str(e)}")
        return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={}) 
""" 