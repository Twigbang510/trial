from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud.crud_conversation import conversation, message
from app.schemas.conversation import ConversationCreate, MessageCreate, ConversationUpdate
from app.models.user import User
from app.core.chat_history import ChatHistoryManager
import logging

logger = logging.getLogger(__name__)

class ConversationService:
    """Service for conversation-related business logic"""
    
    @staticmethod
    def get_or_create_conversation(
        db: Session, 
        conversation_id: Optional[int], 
        user: Optional[User], 
        context: str = "consultant"
    ):
        """Get existing conversation or create new one"""
        if conversation_id:
            conv = conversation.get(db, id=conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
            return conv
        else:
            conv_data = ConversationCreate(
                user_id=getattr(user, 'id') if user else None,
                context=context
            )
            return conversation.create(db, obj_in=conv_data)
    
    @staticmethod
    def validate_conversation_access(conv, user: Optional[User]) -> None:
        """Validate user access to conversation"""
        if user and getattr(conv, 'user_id') and int(getattr(conv, 'user_id')) != int(getattr(user, 'id')):
            raise HTTPException(status_code=403, detail="Access denied")
    
    @staticmethod
    def check_conversation_completed(conv) -> bool:
        """Check if conversation is already completed"""
        return getattr(conv, 'booking_status') == 'complete'
    
    @staticmethod
    def save_user_message(db: Session, content: str, conversation_id: int):
        """Save user message to database"""
        user_message = MessageCreate(
            content=content,
            sender="user",
            is_appropriate=True
        )
        return message.create(db, obj_in=user_message, conversation_id=conversation_id)
    
    @staticmethod
    def save_bot_message(db: Session, content: str, conversation_id: int):
        """Save bot message to database"""
        bot_message = MessageCreate(
            content=content,
            sender="bot",
            is_appropriate=True
        )
        return message.create(db, obj_in=bot_message, conversation_id=conversation_id)
    
    @staticmethod
    def get_conversation_history(db: Session, conversation_id: int) -> List:
        """Get conversation message history"""
        db_messages = message.get_by_conversation(db, conversation_id=conversation_id)
        return db_messages[:-1] if db_messages else []
    
    @staticmethod
    def should_stop_conversation(conv, future_bot_count: int) -> bool:
        """Check if conversation should be stopped due to limits"""
        return ChatHistoryManager.should_stop_conversation(conv, future_bot_count)
    
    @staticmethod
    def abandon_conversation(db: Session, conv) -> str:
        """Mark conversation as abandoned and return stop message"""
        if getattr(conv, 'booking_status') != "abandoned":
            setattr(conv, 'booking_status', "abandoned")
            conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(booking_status="abandoned"))
        
        return ChatHistoryManager.get_stop_message()
    
    @staticmethod
    def update_conversation_title(db: Session, conv, first_message: str) -> None:
        """Update conversation title if not set"""
        if not getattr(conv, 'title'):
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message
            conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(title=title))
    
    @staticmethod
    def increment_bot_response_count(db: Session, conv) -> None:
        """Increment bot response count for conversation"""
        ChatHistoryManager.increment_bot_response_count(db, conv)
    
    @staticmethod
    def format_conversation_for_processing(historical_messages: List) -> str:
        """Format conversation history for AI processing"""
        return ChatHistoryManager.convert_messages_to_history_string(historical_messages)
    
    @staticmethod
    def update_conversation_status(db: Session, conv, user_message: str, conversation_history: str) -> None:
        """Update conversation status based on user message"""
        ChatHistoryManager.update_conversation_status(db, conv, user_message, conversation_history) 