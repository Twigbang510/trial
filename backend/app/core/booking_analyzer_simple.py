from typing import Text, Dict, List, Optional
from datetime import datetime, date
import re
import asyncio
import logging
import json
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class BookingAnalyzerSimple:
    """
    Simple Booking Analysis Engine using JSON response instead of function calling
    """
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.0-flash')
    
    # =================== PROMPTS ===================
    
    def get_intent_analysis_prompt(self) -> str:
        """Prompt for intent classification with JSON response"""
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

Respond ONLY with a valid JSON object in this exact format:
{
  "intent": "A|C|O",
  "safety_score": 1-99,
  "is_rejection": true/false,
  "is_confirmation": true/false,
  "reasoning": "Brief explanation (max 3 lines)"
}
"""

    def get_time_extraction_prompt(self) -> str:
        """Prompt for time extraction with JSON response"""
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

Respond ONLY with a valid JSON object in this exact format:
{
  "input_slots": ["08:15", "14:00"],
  "time_range": ["08:00", "10:00"],
  "date": "2025-01-27",
  "date_expressions": ["today", "tomorrow"],
  "reasoning": "Brief explanation (max 2 lines)"
}
"""

    # =================== CORE ANALYSIS METHODS ===================
    
    async def analyze_intent(self, user_message: str, conversation_history: str) -> Dict:
        """Analyze user intent for booking classification"""
        context = f"""
## CURRENT USER MESSAGE:
{user_message}

## CONVERSATION HISTORY:
{conversation_history}

## ANALYSIS TASK:
Classify the user's intent and provide safety analysis for this booking conversation.
"""
        
        try:
            full_prompt = f"{self.get_intent_analysis_prompt()}\n\n{context}"
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=512,
                )
            )
            
            # Parse JSON response
            result = self._parse_json_response(response.text)
            return self._validate_intent_result(result)
            
        except Exception as e:
            logger.warning(f"Intent analysis failed, using manual parsing: {e}")
            # Fallback: Manual analysis for common cases
            return self._manual_intent_analysis(user_message)
    
    async def extract_time_info(self, user_message: str, conversation_history: str) -> Dict:
        """Extract time information from user message"""
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
            full_prompt = f"{self.get_time_extraction_prompt()}\n\n{context}"
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=512,
                )
            )
            
            # Parse JSON response
            result = self._parse_json_response(response.text)
            return self._process_time_result(result)
            
        except Exception as e:
            logger.warning(f"Time extraction failed, using manual parsing: {e}")
            # Fallback: Manual time extraction
            return self._manual_time_extraction(user_message)
    
    async def analyze_complete(self, user_message: str, conversation_history: str) -> Dict:
        """Complete analysis combining intent classification and time extraction"""
        try:
            # Run both analyses in parallel
            intent_task = self.analyze_intent(user_message, conversation_history)
            time_task = self.extract_time_info(user_message, conversation_history)
            
            intent_result, time_result = await asyncio.gather(intent_task, time_task)
            
            # Combine results
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
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from Gemini response"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_text = response_text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].strip()
            
            result = json.loads(json_text)
            if isinstance(result, dict):
                return result
            else:
                return {}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}, response: {response_text[:200]}")
            return {}
    
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
        
        return time_str
    
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
    
    def _manual_intent_analysis(self, user_message: str) -> Dict:
        """Manual intent analysis as fallback"""
        message_lower = user_message.lower()
        
        # Check for agreement keywords
        agreement_keywords = ["được", "đồng ý", "ok", "xác nhận", "yes", "sounds good", "that works"]
        confirmation_keywords = ["chọn", "xác nhận", "đồng ý slot", "ok slot"]
        
        # Check for checking/questioning keywords  
        checking_keywords = ["còn giờ nào", "thời gian nào", "slot nào", "được không", "có thể"]
        
        # Check for booking request keywords (intent A)
        booking_keywords = ["đặt lịch", "book", "hẹn", "appointment", "muốn đặt", "tôi muốn"]
        
        # Check for rejection keywords
        rejection_keywords = ["không", "không được", "bận", "không thể", "từ chối"]
        
        if any(keyword in message_lower for keyword in agreement_keywords):
            intent = "A"
            safety_score = 25 if any(keyword in message_lower for keyword in confirmation_keywords) else 35
            is_confirmation = any(keyword in message_lower for keyword in confirmation_keywords)
            is_rejection = False
        elif any(keyword in message_lower for keyword in checking_keywords):
            intent = "C"
            safety_score = 45
            is_confirmation = False
            is_rejection = False
        elif any(keyword in message_lower for keyword in booking_keywords):
            # User wants to book appointment with specific time
            intent = "A"
            safety_score = 30
            is_confirmation = False
            is_rejection = False
        elif any(keyword in message_lower for keyword in rejection_keywords):
            intent = "A"  # Still booking related but rejection
            safety_score = 75
            is_confirmation = False
            is_rejection = True
        else:
            intent = "O"
            safety_score = 50
            is_confirmation = False
            is_rejection = False
        
        return {
            "intent": intent,
            "safety_score": safety_score,
            "is_rejection": is_rejection,
            "is_confirmation": is_confirmation,
            "reasoning": f"Manual analysis: {intent} intent detected from message content"
        }
    
    def _manual_time_extraction(self, user_message: str) -> Dict:
        """Manual time extraction as fallback"""
        input_slots = []
        time_range = []
        date = None
        date_expressions = []
        
        # Extract time patterns with specific handling
        # Pattern 1: Hours with minutes (8h15, 8:15)
        pattern1_matches = re.findall(r'\b(\d{1,2})[h:](\d{2})\b', user_message)
        for hour, minute in pattern1_matches:
            time_str = f"{int(hour):02d}:{minute}"
            if time_str not in input_slots:
                input_slots.append(time_str)
        
        # Pattern 2: Just hours (6h, 14h)
        pattern2_matches = re.findall(r'\b(\d{1,2})h\b', user_message)
        for hour in pattern2_matches:
            time_str = f"{int(hour):02d}:00"
            if time_str not in input_slots:
                input_slots.append(time_str)
        
        # Pattern 3: Time as numbers (815, 1430)
        pattern3_matches = re.findall(r'\b(\d{3,4})\b', user_message)
        for time_num in pattern3_matches:
            if len(time_num) >= 3:
                hour = time_num[:-2] or "0"
                minute = time_num[-2:]
                time_str = f"{int(hour):02d}:{minute}"
                if time_str not in input_slots:
                    input_slots.append(time_str)
        
        # Check for time range keywords
        if "từ" in user_message and "đến" in user_message:
            # Try to extract range
            range_pattern = r'từ\s*(\d{1,2})[h:]?(\d{2})?\s*đến\s*(\d{1,2})[h:]?(\d{2})?'
            match = re.search(range_pattern, user_message)
            if match:
                start_hour = int(match.group(1))
                start_min = match.group(2) or "00"
                end_hour = int(match.group(3))
                end_min = match.group(4) or "00"
                time_range = [f"{start_hour:02d}:{start_min}", f"{end_hour:02d}:{end_min}"]
        
        # Check for date expressions
        if "hôm nay" in user_message or "today" in user_message:
            date_expressions.append("today")
            date = datetime.now().strftime("%Y-%m-%d")
        elif "ngày mai" in user_message or "tomorrow" in user_message:
            date_expressions.append("tomorrow")
            from datetime import timedelta
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        return {
            "input_slots": input_slots,
            "time_range": time_range,
            "date": date,
            "date_expressions": date_expressions,
            "reasoning": f"Manual extraction: found {len(input_slots)} time slots, range: {len(time_range)//2 if time_range else 0}"
        }

# Singleton instance
booking_analyzer_simple = BookingAnalyzerSimple() 
 