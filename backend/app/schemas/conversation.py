from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    sender: str
    is_appropriate: Optional[bool] = True

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_appropriate: Optional[bool] = None

class MessageInDB(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None
    context: Optional[str] = "consultant"
    bot_response_count: int = 0
    booking_status: str = "ongoing"

class ConversationCreate(ConversationBase):
    user_id: Optional[int] = None

class ConversationUpdate(ConversationBase):
    booking_status: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    user_id: Optional[int]
    bot_response_count: int = 0
    booking_status: str = "ongoing"
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class ConversationInDB(ConversationBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    title: Optional[str] = None
    context: str
    bot_response_count: int
    booking_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = None  # For list views
    last_message: Optional[str] = None   # For list views

    class Config:
        from_attributes = True

class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int
    skip: int
    limit: int

class BookingOption(BaseModel):
    """Schema for booking time slot options"""
    type: str  # "exact_match" or "alternative"
    lecturer_name: str
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    subject: str
    location: str
    duration_minutes: int
    availability_id: int

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    is_appropriate: bool = True
    moderation_action: Optional[str] = None
    warning_message: Optional[str] = None

class EnhancedChatResponse(ChatResponse):
    booking_options: List[BookingOption] = []
    needs_availability_check: bool = False
    suggested_next_action: str = "provide_info"
    booking_analysis: Optional[dict] = None
    email_sent: Optional[bool] = None
    booking_status: Optional[str] = None 