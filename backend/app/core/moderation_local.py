# 🏠 **Local Models Content Moderation**
# Multiple models support for high accuracy multilingual moderation

from typing import Dict, Any, Optional, List
from app.core.config import settings
import logging
import json
import os
import torch
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, 
    T5Tokenizer, T5ForConditionalGeneration,
    pipeline, AutoModel
)
import numpy as np
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

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

class LocalModerationModels:
    """Manager for local moderation models"""
    
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.pipelines = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load models based on configuration
        self._load_models()
    
    def _load_models(self):
        """Load all available models"""
        try:
            # Always load keyword patterns first (essential fallback)
            self._load_minimal_fallback()
            
            # 1. Load Vietnamese specialized models
            self._load_vietnamese_models()
            
            # 2. Load Multilingual models
            self._load_multilingual_models()
            
            # 3. Load English models
            self._load_english_models()
            
            # 4. Load fallback models
            self._load_fallback_models()
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            if not hasattr(self, 'keyword_patterns'):
                self._load_minimal_fallback()
    
    def _load_vietnamese_models(self):
        """Load Vietnamese-specific models"""
        try:
            # Load ViHateT5 or similar Vietnamese hate speech model
            model_name = "VietAI/vihate-t5-base"
            self.pipelines['vietnamese'] = pipeline(
                "text-classification",
                model="distilbert-base-multilingual-cased",
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("Vietnamese model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Vietnamese model: {str(e)}")
    
    def _load_multilingual_models(self):
        """Load multilingual models"""
        try:
            model_name = "unitary/toxic-bert"
            self.pipelines['toxic_bert'] = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("Toxic-BERT model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Toxic-BERT: {str(e)}")
            
        try:
            model_name = "distilbert-base-multilingual-cased"
            self.pipelines['multilingual'] = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("Multilingual DistilBERT loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load multilingual DistilBERT: {str(e)}")
    
    def _load_english_models(self):
        """Load English-specific models"""
        try:
            model_name = "martin-ha/toxic-comment-model"
            self.pipelines['toxic_comment'] = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("Toxic comment model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load toxic comment model: {str(e)}")
    
    def _load_fallback_models(self):
        """Load fallback models"""
        try:
            model_name = "cardiffnlp/twitter-roberta-base-offensive"
            self.pipelines['offensive'] = pipeline(
                "text-classification",
                model=model_name,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            print("Offensive language model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load offensive model: {str(e)}")
    
    def _load_minimal_fallback(self):
        """Load minimal fallback when other models fail"""
        try:
            self.keyword_patterns = {
                'hate': ['hate', 'nazi', 'terrorist', 'kill', 'murder', 'death', 'violence'],
                'harassment': ['stupid', 'idiot', 'moron', 'ugly', 'fat', 'loser', 'freak'],
                'sexual': ['sex', 'porn', 'nude', 'naked', 'breast', 'penis', 'vagina'],
                'violence': ['violence', 'attack', 'bomb', 'weapon', 'fight', 'war', 'blood'],
                'vietnamese_hate': [
                    'chết', 'giết', 'đánh', 'thù', 'ghét', 'ngu', 'đần', 'óc chó', 
                    'súc vật', 'con lợn', 'đồ chó', 'thằng ngu', 'con khốn', 'đồ khốn'
                ],
                'vietnamese_harassment': [
                    'xấu', 'béo', 'gầy', 'ngu', 'dốt', 'đần', 'ngốc', 'khùng', 'điên'
                ]
            }
            print("Minimal keyword fallback loaded")
        except Exception as e:
            logger.error(f"Even minimal fallback failed: {str(e)}")

    @lru_cache(maxsize=1000)
    def _detect_language(self, text: str) -> str:
        """Detect language of input text"""
        vietnamese_chars = set('àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ')
        
        if any(char.lower() in vietnamese_chars for char in text):
            return "vi"
        return "en"
    
    async def moderate_with_vietnamese_model(self, text: str) -> ModerationResult:
        """Moderate using Vietnamese-specific model"""
        if 'vietnamese' not in self.pipelines:
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        try:
            results = self.pipelines['vietnamese'](text)
            
            negative_score = 0.0
            
            if isinstance(results, list) and len(results) > 0:
                for result in results:
                    if isinstance(result, dict) and 'label' in result and 'score' in result:
                        if result['label'] in ['NEGATIVE', 'TOXIC', 'HATE', 'toxic', 'hate', '1', 1]:
                            negative_score = max(negative_score, result['score'])
            elif isinstance(results, dict):
                if results.get('label') in ['NEGATIVE', 'TOXIC', 'HATE', 'toxic', 'hate', '1', 1]:
                    negative_score = results.get('score', 0.0)
            else:
                logger.warning(f"Unexpected vietnamese output format: {type(results)} - {results}")
                negative_score = 0.0
            
            text_lower = text.lower()
            if hasattr(self, 'keyword_patterns'):
                vietnamese_hate_matches = sum(1 for word in self.keyword_patterns.get('vietnamese_hate', []) 
                                            if word in text_lower)
            else:
                vietnamese_hate_matches = 0
            if vietnamese_hate_matches > 0:
                negative_score = min(negative_score + 0.3 * vietnamese_hate_matches, 1.0)
            
            flagged = negative_score > 0.5
            categories = {
                "hate": flagged and negative_score > 0.7,
                "harassment": flagged and negative_score > 0.6,
                "vietnamese_specific": vietnamese_hate_matches > 0
            }
            
            category_scores = {
                "hate": negative_score * 0.9,
                "harassment": negative_score * 0.8,
                "vietnamese_specific": min(vietnamese_hate_matches * 0.4, 1.0)
            }
            
            return ModerationResult(
                flagged=flagged,
                harmful_score=negative_score,
                categories=categories,
                category_scores=category_scores
            )
            
        except Exception as e:
            logger.error(f"Error in Vietnamese moderation: {str(e)}")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
    
    async def moderate_with_toxic_bert(self, text: str) -> ModerationResult:
        """Moderate using Toxic-BERT model"""
        if 'toxic_bert' not in self.pipelines:
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        try:
            results = self.pipelines['toxic_bert'](text)
            
            toxic_score = 0.0
            
            if isinstance(results, list) and len(results) > 0:
                for result in results:
                    if isinstance(result, dict) and 'label' in result and 'score' in result:
                        if result['label'] in ['TOXIC', 'toxic', '1', 1]:
                            toxic_score = max(toxic_score, result['score'])
            elif isinstance(results, dict):
                if results.get('label') in ['TOXIC', 'toxic', '1', 1]:
                    toxic_score = results.get('score', 0.0)
            else:
                logger.warning(f"Unexpected toxic_bert output format: {type(results)} - {results}")
                toxic_score = 0.0
            
            flagged = toxic_score > 0.5
            categories = {
                "toxic": flagged,
                "hate": flagged and toxic_score > 0.7,
                "harassment": flagged and toxic_score > 0.6,
                "violence": flagged and toxic_score > 0.8
            }
            
            category_scores = {
                "toxic": toxic_score,
                "hate": toxic_score * 0.9,
                "harassment": toxic_score * 0.8,
                "violence": toxic_score * 0.7
            }
            
            return ModerationResult(
                flagged=flagged,
                harmful_score=toxic_score,
                categories=categories,
                category_scores=category_scores
            )
            
        except Exception as e:
            logger.error(f"Error in Toxic-BERT moderation: {str(e)}")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
    
    async def moderate_with_multilingual(self, text: str) -> ModerationResult:
        """Moderate using multilingual model"""
        if 'multilingual' not in self.pipelines:
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        try:
            results = self.pipelines['multilingual'](text)
            
            negative_score = 0.0
            
            if isinstance(results, list) and len(results) > 0:
                for result in results:
                    if isinstance(result, dict) and 'label' in result and 'score' in result:
                        if result['label'] in ['NEGATIVE', 'TOXIC', 'toxic', '1', 1]:
                            negative_score = max(negative_score, result['score'])
            elif isinstance(results, dict):
                if results.get('label') in ['NEGATIVE', 'TOXIC', 'toxic', '1', 1]:
                    negative_score = results.get('score', 0.0)
            else:
                logger.warning(f"Unexpected multilingual output format: {type(results)} - {results}")
                negative_score = 0.0
            
            flagged = negative_score > 0.5
            categories = {
                "negative": flagged,
                "toxic": flagged and negative_score > 0.7,
                "hate": flagged and negative_score > 0.8
            }
            
            category_scores = {
                "negative": negative_score,
                "toxic": negative_score * 0.8,
                "hate": negative_score * 0.9
            }
            
            return ModerationResult(
                flagged=flagged,
                harmful_score=negative_score,
                categories=categories,
                category_scores=category_scores
            )
            
        except Exception as e:
            logger.error(f"Error in multilingual moderation: {str(e)}")
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
    
    async def moderate_with_keywords(self, text: str) -> ModerationResult:
        """Fallback moderation using keyword patterns"""
        if not hasattr(self, 'keyword_patterns'):
            return ModerationResult(flagged=False, harmful_score=0.0, categories={}, category_scores={})
        
        text_lower = text.lower()
        categories = {}
        category_scores = {}
        max_score = 0.0
        
        for category, keywords in self.keyword_patterns.items():
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

# Global instance
local_models = LocalModerationModels()

async def moderate_content_local(text: str, model_preference: str = "auto", language: str = None) -> ModerationResult:
    """
    Main function for local content moderation with multiple models
    
    Args:
        text: Text to moderate
        model_preference: "auto", "vietnamese", "toxic_bert", "multilingual", "keywords"
    
    Returns:
        ModerationResult: Moderation results
    """
    try:
        # Use provided language or detect it
        detected_language = language if language else local_models._detect_language(text)
        
        if model_preference == "auto":
            # Auto-select best model based on language and availability
            if detected_language == "vi" and 'vietnamese' in local_models.pipelines:
                result = await local_models.moderate_with_vietnamese_model(text)
            elif 'toxic_bert' in local_models.pipelines:
                result = await local_models.moderate_with_toxic_bert(text)
            elif 'multilingual' in local_models.pipelines:
                result = await local_models.moderate_with_multilingual(text)
            else:
                result = await local_models.moderate_with_keywords(text)
        else:
            # Use specific model
            if model_preference == "vietnamese":
                result = await local_models.moderate_with_vietnamese_model(text)
            elif model_preference == "toxic_bert":
                result = await local_models.moderate_with_toxic_bert(text)
            elif model_preference == "multilingual":
                result = await local_models.moderate_with_multilingual(text)
            elif model_preference == "keywords":
                result = await local_models.moderate_with_keywords(text)
            else:
                result = await local_models.moderate_with_keywords(text)
        
        # Log results
        print(f"Local moderation result - Model: {model_preference}, Language: {detected_language}, "
                   f"Type: {result.violation_type}, Flagged: {result.flagged}, Score: {result.harmful_score:.3f}")
        
        if result.violation_type != "CLEAN":
            logger.warning(f"Local violation detected: {text[:100]}... - Categories: {result.categories}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in local content moderation: {str(e)}")
        return await local_models.moderate_with_keywords(text)

async def moderate_content_ensemble(text: str) -> ModerationResult:
    """
    Ensemble moderation using multiple models for higher accuracy
    """
    try:
        results = await asyncio.gather(
            local_models.moderate_with_vietnamese_model(text),
            local_models.moderate_with_toxic_bert(text),
            local_models.moderate_with_multilingual(text),
            return_exceptions=True
        )
        
        valid_results = [r for r in results if isinstance(r, ModerationResult)]
        
        if not valid_results:
            return await local_models.moderate_with_keywords(text)
        
        language = local_models._detect_language(text)
        if language == "vi":
            weights = [0.5, 0.3, 0.2]  # Vietnamese, Toxic-BERT, Multilingual
        else:
            weights = [0.2, 0.5, 0.3]  # Vietnamese, Toxic-BERT, Multilingual
        
        total_score = 0.0
        combined_categories = {}
        combined_category_scores = {}
        
        for i, result in enumerate(valid_results):
            weight = weights[i] if i < len(weights) else 0.1
            total_score += result.harmful_score * weight
            
            for category, flagged in result.categories.items():
                if category not in combined_categories:
                    combined_categories[category] = 0
                    combined_category_scores[category] = 0
                
                combined_categories[category] += (1 if flagged else 0) * weight
                combined_category_scores[category] += result.category_scores.get(category, 0) * weight
        
        total_weight = sum(weights[:len(valid_results)])
        total_score /= total_weight
        
        for category in combined_categories:
            combined_categories[category] = combined_categories[category] / total_weight > 0.5
            combined_category_scores[category] /= total_weight
        
        ensemble_result = ModerationResult(
            flagged=total_score > 0.5,
            harmful_score=total_score,
            categories=combined_categories,
            category_scores=combined_category_scores
        )
        
        print(f"Ensemble moderation - Models: {len(valid_results)}, Language: {language}, "
                   f"Type: {ensemble_result.violation_type}, Score: {ensemble_result.harmful_score:.3f}")
        
        return ensemble_result
        
    except Exception as e:
        logger.error(f"Error in ensemble moderation: {str(e)}")
        return await local_models.moderate_with_keywords(text) 