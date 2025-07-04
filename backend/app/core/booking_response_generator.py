from typing import Text, Dict, List, Optional
from datetime import datetime, date, timedelta
import re
import asyncio
import logging
import json
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class BookingResponseGenerator:
    """
    Enhanced Booking System - One API call for Analysis + Response + Availability Matching
    Optimized to reduce token usage while providing comprehensive booking assistance
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.client = genai.GenerativeModel('gemini-2.0-flash')
    
    def get_combined_prompt(self) -> str:
        """Combined prompt for analysis + response generation"""
        return """
You are an AI booking assistant that helps users schedule appointments with lecturers.

ANALYZE the user's message and RESPOND appropriately while providing booking analysis.

**Intent Classification:**
- A (Agreed/Accepted): User confirms/agrees to a time slot
- C (Checking/Continuing): User asks about availability or explores options  
- O (Out of scope): Unrelated to booking

**Safety Score (1-99):**
- 1-20: Very enthusiastic, eager to book
- 21-40: Positive, interested 
- 41-60: Neutral, asking questions
- 61-80: Hesitant, showing resistance
- 81-99: Clear rejection

**Time Extraction Rules:**
- "815" → "08:15", "1430" → "14:30"
- "8h15" → "08:15", "2pm" → "14:00"
- "từ 8h đến 10h" → range ["08:00", "10:00"]
- "hôm nay" → today, "ngày mai" → tomorrow

**Response Guidelines:**
- Be helpful and professional
- If user mentions specific times, acknowledge them
- If asking about availability, offer to check lecturer schedules
- Keep responses concise but informative
- Use Vietnamese when user uses Vietnamese

Respond with a JSON object containing BOTH analysis and response:
```json
{
  "analysis": {
    "intent": "A|C|O",
    "safety_score": 1-99,
    "is_rejection": true/false,
    "is_confirmation": true/false,
    "input_slots": ["08:15", "14:00"],
    "time_range": ["08:00", "10:00"],
    "date": "2025-01-27",
    "reasoning": "Brief explanation"
  },
  "response": {
    "text": "Your helpful response to the user",
    "needs_availability_check": true/false,
    "suggested_next_action": "check_availability|confirm_booking|provide_info"
  }
}
```
"""

    async def process_booking_request(
        self, 
        user_message: str, 
        conversation_history: str,
        db_session = None
    ) -> Dict:
        """
        Process booking request with combined analysis + response + availability matching
        Returns complete response with options
        """
        try:
            ai_result = await self._call_ai_combined(user_message, conversation_history)
            
            analysis = ai_result.get("analysis", {})
            ai_response = ai_result.get("response", {})
            
            booking_options = []
            if ai_response.get("needs_availability_check") and db_session:
                booking_options = await self._find_booking_options(analysis, db_session)
            
            enhanced_response = self._enhance_response_with_options(
                ai_response.get("text", ""), booking_options
            )
            
            return {
                "intent": analysis.get("intent", "O"),
                "safety_score": analysis.get("safety_score", 50),
                "is_rejection": analysis.get("is_rejection", False),
                "is_confirmation": analysis.get("is_confirmation", False),
                "input_slots": analysis.get("input_slots", []),
                "time_range": analysis.get("time_range", []),
                "date": analysis.get("date"),
                "reasoning": analysis.get("reasoning", ""),
                "response_text": enhanced_response,
                "booking_options": booking_options,
                "needs_availability_check": ai_response.get("needs_availability_check", False),
                "suggested_next_action": ai_response.get("suggested_next_action", "provide_info")
            }
            
        except Exception as e:
            logger.error(f"Booking request processing failed: {e}")
            return self._fallback_processing(user_message)
    
    async def _call_ai_combined(self, user_message: str, conversation_history: str) -> Dict:
        """Call AI for combined analysis and response"""
        context = f"""
## CURRENT USER MESSAGE:
{user_message}

## CONVERSATION HISTORY:
{conversation_history}

## TASK:
Analyze the user's booking intent and provide an appropriate response.
"""
        
        try:
            full_prompt = f"{self.get_combined_prompt()}\n\n{context}"
            response = self.client.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                )
            )
            
            result = self._parse_json_response(response.text)
            return result
            
        except Exception as e:
            logger.warning(f"AI call failed, using fallback: {e}")
            return self._manual_combined_processing(user_message)
    
    async def _find_booking_options(self, analysis: Dict, db_session) -> List[Dict]:
        """Find available booking options based on analysis"""
        try:
            from app.crud import lecturer_availability
            ai_date = analysis.get("date")
            input_slots = analysis.get("input_slots", [])
            
            if ai_date:
                target_date = self._parse_target_date(ai_date)
            else:
                target_date = self._parse_target_date(None)
                
            user_slots = input_slots
            user_range = analysis.get("time_range", [])
            booking_options = []
            
            if user_slots:
                matched_slots = lecturer_availability.find_matching_slots(
                    db_session, user_slots, target_date
                )
                for slot in matched_slots:
                    booking_options.append({
                        "type": "exact_match",
                        "lecturer_name": slot["lecturer_name"],
                        "date": slot["date"],
                        "time": slot["time"],
                        "subject": slot["subject"],
                        "location": slot["location"],
                        "duration_minutes": slot["duration_minutes"],
                        "availability_id": slot["availability_id"]
                    })
                    
            if not booking_options:
                if user_range:
                    alternative_slots = lecturer_availability.find_alternative_slots_in_range(
                        db_session, user_range, target_date, limit=5
                    )
                elif not user_slots:
                    alternative_slots = lecturer_availability.find_alternative_slots(
                        db_session, None, target_date, limit=5
                    )
                else:
                    alternative_slots = []
                
                for slot in alternative_slots:
                    booking_options.append({
                        "type": "alternative",
                        "lecturer_name": slot["lecturer_name"],
                        "date": slot["date"], 
                        "time": slot["time"],
                        "subject": slot["subject"],
                        "location": slot["location"],
                        "duration_minutes": slot["duration_minutes"],
                        "availability_id": slot["availability_id"]
                    })
                    
            return booking_options[:8]
        except Exception as e:
            logger.error(f"Booking options search failed: {e}")
            return []
    
    def _parse_target_date(self, date_str: Optional[str]) -> date:
        """Parse target date from analysis or default to next Monday"""
        try:
            if date_str:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                logger.info(f"Parsed date from string '{date_str}': {parsed_date}")
                return parsed_date
            else:
                # Default to next Monday if no date specified
                today = datetime.now().date()
                days_ahead = 0 - today.weekday()  # Monday is 0
                if days_ahead <= 0:  # If today is Monday or past Monday, get next Monday
                    days_ahead += 7
                next_monday = today + timedelta(days_ahead)
                logger.info(f"No date specified, defaulting to next Monday: {next_monday}")
                return next_monday
        except Exception as e:
            logger.warning(f"Date parsing error for '{date_str}': {e}")
            # Fallback to next Monday
            today = datetime.now().date()
            days_ahead = 0 - today.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            fallback_date = today + timedelta(days_ahead)
            logger.info(f"Fallback to next Monday: {fallback_date}")
            return fallback_date
    
    def _enhance_response_with_options(self, base_response: str, booking_options: List[Dict]) -> str:
        """Enhance AI response - only show alternatives when no exact matches"""
        
        # Phân loại booking options
        exact_matches = [opt for opt in booking_options if opt["type"] == "exact_match"]
        alternatives = [opt for opt in booking_options if opt["type"] == "alternative"]
        
        # Nếu có exact matches, chỉ trả về response gốc
        # (Frontend sẽ hiển thị nút bên ngoài chat)
        if exact_matches:
            enhanced_response = base_response + "\n\n✅ **Tìm thấy khung giờ phù hợp!**\n"
            enhanced_response += "Vui lòng chọn khung giờ bạn muốn từ các lựa chọn bên dưới."
            return enhanced_response
        
        # Nếu không có exact matches nhưng có alternatives
        if alternatives:
            no_exact_message = "\n\n❌ **Không có thời gian nào trùng khớp chính xác**\n"
            no_exact_message += "Tuy nhiên, tôi tìm thấy một số khung giờ gần với thời gian bạn yêu cầu:\n\n"
            
            # Hiển thị alternatives trong response text
            for i, opt in enumerate(alternatives[:5], 1):
                no_exact_message += f"{i}. **{opt['time']}** - {opt['lecturer_name']}\n"
                no_exact_message += f"   📚 {opt['subject']} | 📍 {opt['location']} | ⏱️ {opt['duration_minutes']} phút\n"
                no_exact_message += f"   📅 {opt['date']}\n\n"
            
            no_exact_message += "💡 **Nhấn vào khung giờ bạn muốn để đặt lịch!**"
            return base_response + no_exact_message
        
        # Nếu không có slot nào
        no_match_message = "\n\n❌ **Không có thời gian nào trùng khớp**\n"
        no_match_message += "Rất tiếc, không có giảng viên nào rảnh vào thời gian bạn yêu cầu. \n"
        no_match_message += "Bạn có thể:\n"
        no_match_message += "• Thử thời gian khác (ví dụ: sáng thứ 2, chiều thứ 3)\n"
        no_match_message += "• Hỏi về lịch trống của giảng viên\n"
        no_match_message += "• Đặt lịch vào tuần sau\n\n"
        no_match_message += "💡 Hãy cho tôi biết thời gian khác bạn có thể sắp xếp!"
        return base_response + no_match_message
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON from AI response"""
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
            logger.warning(f"JSON parsing failed: {e}")
            return {}
    
    def _manual_combined_processing(self, user_message: str) -> Dict:
        """Manual processing as fallback"""
        # Reuse logic from simple analyzer
        from app.core.booking_analyzer_optimized import booking_analyzer_optimized
        
        # Manual analysis using optimized analyzer
        intent_result = booking_analyzer_optimized._enhanced_manual_intent_analysis(user_message)
        time_result = booking_analyzer_optimized._enhanced_manual_time_extraction(user_message)
        
        # Generate simple response
        response_text = self._generate_simple_response(intent_result["intent"], user_message)
        
        return {
            "analysis": {
                "intent": intent_result["intent"],
                "safety_score": intent_result["safety_score"],
                "is_rejection": intent_result["is_rejection"],
                "is_confirmation": intent_result["is_confirmation"],
                "input_slots": time_result["input_slots"],
                "time_range": time_result["time_range"],
                "date": time_result["date"],
                "reasoning": f"Fallback: {intent_result['reasoning']}"
            },
            "response": {
                "text": response_text,
                "needs_availability_check": intent_result["intent"] in ["A", "C"],
                "suggested_next_action": "check_availability" if intent_result["intent"] == "C" else "confirm_booking"
            }
        }
    
    def _generate_simple_response(self, intent: str, user_message: str) -> str:
        """Generate simple response based on intent"""
        if intent == "A":
            return "Cảm ơn bạn! Tôi sẽ kiểm tra lịch trống của các giảng viên cho khung giờ bạn yêu cầu."
        elif intent == "C":
            return "Tôi sẽ kiểm tra các khung giờ có sẵn của giảng viên cho bạn."
        else:
            return "Tôi có thể giúp bạn đặt lịch hẹn với giảng viên. Bạn muốn đặt lịch vào thời gian nào?"
    
    def _fallback_processing(self, user_message: str) -> Dict:
        """Complete fallback when everything fails"""
        return {
            "intent": "O",
            "safety_score": 50,
            "is_rejection": False,
            "is_confirmation": False,
            "input_slots": [],
            "time_range": [],
            "date": None,
            "reasoning": "Fallback processing due to system error",
            "response_text": "Xin lỗi, có lỗi xảy ra. Bạn có thể thử lại không?",
            "booking_options": [],
            "needs_availability_check": False,
            "suggested_next_action": "provide_info"
        }

def parse_vietnamese_date(user_message: str, input_slots: list) -> date:
    """
    Parse Vietnamese date expressions from user_message.
    Supports: 'thứ 2', 'ngày mai', 'ngày mốt', 'hôm nay', 't4 tới', 'ngày dd/mm', ...
    If only time is given, decide today/tomorrow based on current time.
    """
    user_message = user_message.lower()
    today = datetime.now().date()
    now = datetime.now()
    weekday_map = {
        'thứ 2': 0, 'thứ hai': 0,
        'thứ 3': 1, 'thứ ba': 1,
        'thứ 4': 2, 'thứ tư': 2, 'thứ bốn': 2,
        'thứ 5': 3, 'thứ năm': 3,
        'thứ 6': 4, 'thứ sáu': 4,
        'thứ 7': 5, 'thứ bảy': 5,
        'chủ nhật': 6
    }
    # 1. Ngày cụ thể dạng dd/mm hoặc dd-mm
    match = re.search(r'ngày\s*(\d{1,2})[/-](\d{1,2})', user_message)
    if match:
        day, month = int(match.group(1)), int(match.group(2))
        year = today.year
        # Nếu tháng đã qua thì lấy năm sau
        if month < today.month or (month == today.month and day < today.day):
            year += 1
        try:
            return datetime(year, month, day).date()
        except:
            pass
    # 2. Ngày mai, ngày mốt, hôm nay
    if 'ngày mai' in user_message:
        return today + timedelta(days=1)
    if 'ngày mốt' in user_message:
        return today + timedelta(days=2)
    if 'hôm nay' in user_message:
        return today
    # 3. Thứ trong tuần (thứ 2, thứ 3, ... chủ nhật)
    for key, weekday in weekday_map.items():
        if key in user_message:
            days_ahead = (weekday - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7  # Nếu hôm nay là đúng thứ đó, lấy tuần sau
            return today + timedelta(days=days_ahead)
    # 4. "t4 tới", "t2 tới", ...
    match = re.search(r't(\d)\s*tới', user_message)
    if match:
        weekday = int(match.group(1)) - 2  # t2 = 0
        days_ahead = (weekday - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        return today + timedelta(days=days_ahead)
    # 5. Nếu chỉ có giờ (input_slots) → quyết định hôm nay/mai
    if input_slots:
        try:
            slot_time = datetime.strptime(input_slots[0], "%H:%M").time()
            now_time = now.time()
            if slot_time <= now_time:
                # Nếu giờ đã qua, lấy ngày mai
                return today + timedelta(days=1)
            else:
                return today
        except:
            pass
    # 6. Không nhận diện được, trả về None
    return None

# Singleton instance
booking_response_generator = BookingResponseGenerator() 
 