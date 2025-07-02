from typing import List, Dict, Text, Optional
from sqlalchemy.orm import Session
from app.models.conversation import Conversation
from app.models.message import Message
import logging

logger = logging.getLogger(__name__)

class ChatHistoryManager:
    """Manages chat history and conversation flow logic"""
    
    MAX_BOT_RESPONSES = 5
    BUSY_MESSAGE = "Looks like you are busy or haven't chosen a time slot yet. I'll stop here, you can text back later!"
    
    @staticmethod
    def analyze_conversation_history(messages: List[Message]) -> Dict:
        """
        Analyze conversation history similar to backend old's progress_chat_history
        Returns analysis including bot response count and conversation flow
        """
        system_events = []  # Bot messages
        user_events = []    # User messages
        
        for message in messages:
            if message.sender == "bot":
                system_events.append(message.content)
            else:
                user_events.append(message.content)
        
        return {
            "bot_response_count": len(system_events),
            "user_message_count": len(user_events),
            "system_events": system_events,
            "user_events": user_events,
            "total_messages": len(messages)
        }
    
    @staticmethod
    def convert_messages_to_history_string(messages: List[Message]) -> Text:
        """
        Convert messages to chat history string format
        Similar to backend old's convert_chat_history_dict_to_str
        """
        history_text = ""
        for message in messages:
            role = "bot" if message.sender == "bot" else "user"
            history_text += f"\n{role}: {message.content}"
        
        return history_text.strip()
    
    @staticmethod
    def should_stop_conversation(conversation: Conversation, current_bot_count: int) -> bool:
        """
        Check if conversation should be stopped based on response count and booking status
        """
        # If already abandoned, always stop (no more messages allowed)
        if conversation.booking_status == "abandoned":
            return True
            
        # If already completed booking, don't stop (allow continued conversation)
        if conversation.booking_status == "completed":
            return False
            
        # If ongoing and reached max responses, should stop
        if current_bot_count >= ChatHistoryManager.MAX_BOT_RESPONSES and conversation.booking_status == "ongoing":
            return True
            
        return False
    
    @staticmethod
    def detect_booking_completion(user_message: str, conversation_history: str) -> bool:
        """
        Detect if user has completed booking based on message content
        This is simplified - in real scenario you'd use AI classification like backend old
        """
        # Simple keyword detection for booking completion
        completion_indicators = [
            "yes", "okay", "ok", "confirm", "confirmed", "agree", "agreed",
            "book it", "schedule it", "that works", "perfect", "sounds good",
            "đồng ý", "được", "ok", "xác nhận", "đặt lịch"
        ]
        
        user_message_lower = user_message.lower().strip()
        
        # Check for explicit confirmation
        for indicator in completion_indicators:
            if indicator in user_message_lower:
                return True
                
        return False
    
    @staticmethod
    def update_conversation_status(
        db: Session, 
        conversation: Conversation, 
        user_message: str, 
        conversation_history: str
    ) -> Conversation:
        """
        Update conversation booking status and bot response count
        """
        # Check if booking is completed
        if ChatHistoryManager.detect_booking_completion(user_message, conversation_history):
            setattr(conversation, 'booking_status', 'completed')
            logger.info(f"Conversation {getattr(conversation, 'id', None)} marked as completed booking")
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def increment_bot_response_count(db: Session, conversation: Conversation) -> Conversation:
        """
        Increment bot response count after generating AI response
        """
        setattr(conversation, 'bot_response_count', getattr(conversation, 'bot_response_count', 0) + 1)
        
        # Mark as abandoned if reached max without booking
        if (getattr(conversation, 'bot_response_count', 0) >= ChatHistoryManager.MAX_BOT_RESPONSES and 
            getattr(conversation, 'booking_status', None) == "ongoing"):
            setattr(conversation, 'booking_status', 'abandoned')
            logger.info(f"Conversation {getattr(conversation, 'id', None)} marked as abandoned after {getattr(conversation, 'bot_response_count', 0)} responses")
        
        db.commit()
        db.refresh(conversation)
        return conversation
    
    @staticmethod
    def get_stop_message() -> str:
        """
        Get the message to send when stopping conversation due to max responses
        """
        return ChatHistoryManager.BUSY_MESSAGE
    
    @staticmethod
    def format_conversation_for_ai(messages: List[Message]) -> List[Dict]:
        """
        Format conversation history for AI processing
        """
        formatted_history = []
        for message in messages:
            formatted_history.append({
                "content": message.content,
                "sender": message.sender,
                "timestamp": message.created_at.isoformat() if message.created_at else None
            })
        
        return formatted_history 