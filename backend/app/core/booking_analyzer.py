from typing import Text, Dict, List, Optional
from datetime import datetime, date
import re
import asyncio
import logging
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class BookingAnalyzer:
    """
    Booking Analysis Engine for Intent Classification and Time Extraction
    Based on TrialResponse backend architecture with improvements
    """
    
    def __init__(self):
        # Configure Gemini directly
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.0-flash')
    
    # =================== FUNCTION CALLING DEFINITIONS ===================
    
    @property
    def intent_classifier_function(self) -> Dict:
        """Intent classification function definition"""
        return {
            "name": "classify_booking_intent",
            "description": "Classifies user's message intent for appointment booking into A, C, or O with safety analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "intent": {
                        "type": "string", 
                        "description": "Booking intent classification",
                        "enum": ["A", "C", "O"]
                    },
                    "safety_score": {
                        "type": "integer",
                        "description": "Safety score from 1-99 (1=very willing, 99=clear rejection)",
                        "minimum": 1,
                        "maximum": 99
                    },
                    "is_rejection": {
                        "type": "boolean",
                        "description": "True if user clearly rejects, avoids, or shows no intention to continue"
                    },
                    "is_confirmation": {
                        "type": "boolean", 
                        "description": "True if user clearly confirms a specific time slot"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation for the classification (max 3 lines)"
                    }
                },
                "required": ["intent", "safety_score", "is_rejection", "is_confirmation", "reasoning"]
            }
        }
    
    @property 
    def time_extractor_function(self) -> Dict:
        """Time information extraction function definition"""
        return {
            "name": "extract_time_information",
            "description": "Extracts time-related information from user message including slots, ranges, and dates",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_slots": {
                        "type": "array",
                        "description": "Specific times mentioned by user in HH:mm format",
                        "items": {"type": "string"}
                    },
                    "time_range": {
                        "type": "array", 
                        "description": "Time range if user says 'from X to Y' in [start, end] format",
                        "items": {"type": "string"},
                        "maxItems": 2
                    },
                    "date": {
                        "type": "string",
                        "description": "Date mentioned by user in YYYY-MM-DD format, or null if not specified"
                    },
                    "date_expressions": {
                        "type": "array",
                        "description": "Natural date expressions like 'today', 'tomorrow', 'next week'",
                        "items": {"type": "string"}
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of time extraction (max 2 lines)"
                    }
                },
                "required": ["input_slots", "time_range", "date", "date_expressions", "reasoning"]
            }
        }
    
    # =================== PROMPTS ===================
    
    @property
    def intent_classification_prompt(self) -> str:
        """Prompt for intent classification"""
        return """
You are an AI assistant specialized in analyzing booking appointment conversations.

Classify the user's message intent into exactly one of these categories:

**A (Agreed/Accepted)**: 
- User clearly agrees to a time slot or confirms an appointment
- Shows clear acceptance: "yes", "ok", "sounds good", "that works", "let's do it"
- Vietnamese: "được", "đồng ý", "ok luôn", "tốt", "xác nhận"

**C (Checking/Continuing)**:
- User asks about different times or availability  
- Wants to explore options: "what about...", "do you have...", "can we do..."
- Shows interest but needs more information
- Vietnamese: "còn giờ nào khác không", "thứ 2 được không", "sáng được không"

**O (Out of scope)**:
- Completely unrelated to booking appointments
- General questions, greetings, complaints, irrelevant topics
- User clearly rejects or shows no interest in booking

**Safety Score Guidelines (1-99)**:
- 1-20: Very enthusiastic, eager to book
- 21-40: Positive, interested in booking
- 41-60: Neutral, asking questions
- 61-80: Hesitant, showing some resistance  
- 81-99: Clear rejection or avoidance

Analyze the ENTIRE conversation context, not just the latest message.
"""

    @property
    def time_extraction_prompt(self) -> str:
        """Prompt for time extraction"""
        return """
You are an AI assistant specialized in extracting time information from booking conversations.

Extract all time-related information from the user's message:

**Time Normalization Rules**:
- "815" or "8:15" → "08:15" 
- "2pm" or "14h" → "14:00"
- "8h30" or "8:30am" → "08:30"
- Always use 24-hour format HH:mm

**Date Processing**:
- "today" → current date in YYYY-MM-DD
- "tomorrow" → next day in YYYY-MM-DD  
- "30/6" or "6/30" → "2025-06-30" (assume current year)
- "thứ 2" (Monday), "thứ 3" (Tuesday) → next occurrence

**Time Ranges**:
- "từ 8h đến 10h" → ["08:00", "10:00"]
- "between 2pm and 4pm" → ["14:00", "16:00"]
- "morning" → ["08:00", "12:00"]
- "afternoon" → ["12:00", "18:00"]

**Vietnamese Time Expressions**:
- "sáng" (morning), "chiều" (afternoon), "tối" (evening)
- "hôm nay" (today), "ngày mai" (tomorrow)
- "tuần sau" (next week), "tháng sau" (next month)

Focus on EXPLICIT times mentioned by the user. Don't infer times not clearly stated.
"""

    # =================== CORE ANALYSIS METHODS ===================
    
    async def analyze_intent(self, user_message: str, conversation_history: str) -> Dict:
        """
        Analyze user intent for booking classification
        Returns: {intent, safety_score, is_rejection, is_confirmation, reasoning}
        """
        context = f"""
        ## CURRENT USER MESSAGE:
        {user_message}
        
        ## CONVERSATION HISTORY:
        {conversation_history}
        
        ## ANALYSIS TASK:
        Classify the user's intent and provide safety analysis for this booking conversation.
        """
        
        try:
            result = await self._call_gemini_function(
                context=context,
                system_prompt=self.intent_classification_prompt,
                function_def=self.intent_classifier_function
            )
            
            # Validate and format result
            return self._validate_intent_result(result)
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return self._default_intent_result()
    
    async def extract_time_info(self, user_message: str, conversation_history: str) -> Dict:
        """
        Extract time information from user message
        Returns: {input_slots, time_range, date, date_expressions, reasoning}
        """
        context = f"""
        ## CURRENT USER MESSAGE:
        {user_message}
        
        ## CONVERSATION HISTORY:
        {conversation_history}
        
        ## EXTRACTION TASK:
        Extract all time-related information from the user's message.
        Normalize times to HH:mm format and dates to YYYY-MM-DD format.
        """
        
        try:
            result = await self._call_gemini_function(
                context=context,
                system_prompt=self.time_extraction_prompt,
                function_def=self.time_extractor_function
            )
            
            # Post-process and normalize extracted times
            return self._process_time_result(result)
            
        except Exception as e:
            logger.error(f"Time extraction failed: {e}")
            return self._default_time_result()
    
    async def analyze_complete(self, user_message: str, conversation_history: str) -> Dict:
        """
        Complete analysis combining intent classification and time extraction
        Returns combined result matching user's requested format
        """
        try:
            # Run both analyses in parallel for efficiency
            intent_task = self.analyze_intent(user_message, conversation_history)
            time_task = self.extract_time_info(user_message, conversation_history)
            
            intent_result, time_result = await asyncio.gather(intent_task, time_task)
            
            # Combine results in user's requested format
            combined_result = {
                "intent": intent_result["intent"],
                "safety_score": intent_result["safety_score"], 
                "is_rejection": intent_result["is_rejection"],
                "is_confirmation": intent_result["is_confirmation"],
                "input_slots": time_result["input_slots"],
                "time_range": time_result["time_range"], 
                "date": time_result["date"],
                "reasoning": f"Intent: {intent_result['reasoning']} | Time: {time_result['reasoning']}"
            }
            
            logger.info(f"Booking analysis completed: {combined_result}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Complete analysis failed: {e}")
            return self._default_complete_result()
    
    # =================== HELPER METHODS ===================
    
    async def _call_gemini_function(self, context: str, system_prompt: str, function_def: Dict, retries: int = 3) -> Dict:
        """Call Gemini with function calling"""
        for attempt in range(retries):
            try:
                # Construct the full prompt
                full_prompt = f"{system_prompt}\n\n{context}"
                
                # Create tool from function definition
                tool = genai.protos.Tool(
                    function_declarations=[
                        genai.protos.FunctionDeclaration(
                            name=function_def["name"],
                            description=function_def["description"],
                            parameters=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    key: genai.protos.Schema(
                                        type=genai.protos.Type.STRING if prop.get("type") == "string" 
                                        else genai.protos.Type.INTEGER if prop.get("type") == "integer"
                                        else genai.protos.Type.BOOLEAN if prop.get("type") == "boolean"
                                        else genai.protos.Type.ARRAY if prop.get("type") == "array"
                                        else genai.protos.Type.STRING,
                                        description=prop.get("description", ""),
                                        enum=prop.get("enum", []) if prop.get("enum") else None,
                                        items=genai.protos.Schema(type=genai.protos.Type.STRING) if prop.get("type") == "array" else None
                                    )
                                    for key, prop in function_def["parameters"]["properties"].items()
                                },
                                required=function_def["parameters"].get("required", [])
                            )
                        )
                    ]
                )
                
                # Make the API call with function calling
                response = self.client.generate_content(
                    full_prompt,
                    tools=[tool],
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        top_k=3,
                        max_output_tokens=1024,
                    )
                )
                
                # Extract function call result
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            # Convert function call args to dict
                            args_dict = {}
                            for key, value in part.function_call.args.items():
                                args_dict[key] = value
                            return args_dict
                
                # Fallback to text response
                return {"error": "No function call in response", "text": response.text}
                
            except Exception as e:
                logger.warning(f"Gemini call attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(1)
                else:
                    # If all retries fail, try simpler approach
                    try:
                        # Fallback: Use simple generation without function calling
                        simple_response = self.client.generate_content(
                            f"{system_prompt}\n\n{context}\n\nPlease respond in JSON format with the requested fields."
                        )
                        logger.info("Using fallback simple generation")
                        return {"error": "Function calling failed", "text": str(simple_response.text)}
                    except Exception as final_e:
                        logger.error(f"Final fallback also failed: {final_e}")
                        return {"error": "All attempts failed", "text": str(final_e)}
        return {"error": "Unknown error in _call_gemini_function"}
    
    def _normalize_time(self, time_str: str) -> Optional[str]:
        """Normalize time string to HH:mm format"""
        if not time_str:
            return None
            
        time_str = time_str.strip().lower()
        
        # Handle various time formats
        patterns = [
            (r'^(\d{1,2}):(\d{2})$', lambda m: f"{int(m.group(1)):02d}:{m.group(2)}"),
            (r'^(\d{3,4})$', lambda m: f"{m.group(1)[:-2].zfill(2)}:{m.group(1)[-2:]}"),
            (r'^(\d{1,2})h(\d{2})?$', lambda m: f"{int(m.group(1)):02d}:{m.group(2) or '00'}"),
            (r'^(\d{1,2})\s*(am|pm)$', lambda m: self._convert_12h_to_24h(int(m.group(1)), m.group(2))),
        ]
        
        for pattern, converter in patterns:
            match = re.match(pattern, time_str)
            if match:
                try:
                    return converter(match)
                except:
                    continue
        
        return time_str  # Return original if no pattern matches
    
    def _convert_12h_to_24h(self, hour: int, period: str) -> str:
        """Convert 12-hour format to 24-hour format"""
        if period.lower() == 'pm' and hour != 12:
            hour += 12
        elif period.lower() == 'am' and hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    
    def _validate_intent_result(self, result: Dict) -> Dict:
        """Validate and clean intent analysis result"""
        return {
            "intent": result.get("intent", "O"),
            "safety_score": max(1, min(99, result.get("safety_score", 50))),
            "is_rejection": bool(result.get("is_rejection", False)),
            "is_confirmation": bool(result.get("is_confirmation", False)), 
            "reasoning": result.get("reasoning", "Unable to analyze intent")[:200]
        }
    
    def _process_time_result(self, result: Dict) -> Dict:
        """Process and normalize time extraction result"""
        # Normalize time slots
        input_slots = []
        for slot in result.get("input_slots", []):
            normalized = self._normalize_time(slot)
            if normalized:
                input_slots.append(normalized)
        
        # Normalize time range
        time_range = []
        for time_str in result.get("time_range", []):
            normalized = self._normalize_time(time_str)
            if normalized:
                time_range.append(normalized)
        
        return {
            "input_slots": input_slots,
            "time_range": time_range if len(time_range) == 2 else [],
            "date": result.get("date"),
            "date_expressions": result.get("date_expressions", []),
            "reasoning": result.get("reasoning", "No time information extracted")[:150]
        }
    
    def _default_intent_result(self) -> Dict:
        """Default result when intent analysis fails"""
        return {
            "intent": "O",
            "safety_score": 50,
            "is_rejection": False,
            "is_confirmation": False,
            "reasoning": "Analysis failed - using default values"
        }
    
    def _default_time_result(self) -> Dict:
        """Default result when time extraction fails"""
        return {
            "input_slots": [],
            "time_range": [],
            "date": None,
            "date_expressions": [],
            "reasoning": "Time extraction failed"
        }
    
    def _default_complete_result(self) -> Dict:
        """Default result when complete analysis fails"""
        return {
            "intent": "O",
            "safety_score": 50,
            "is_rejection": False,
            "is_confirmation": False,
            "input_slots": [],
            "time_range": [],
            "date": None,
            "reasoning": "Complete analysis failed - using default values"
        }

# Singleton instance
booking_analyzer = BookingAnalyzer() 
 