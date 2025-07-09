from pydantic import BaseModel, field_validator, ConfigDict
from typing import List, Optional, Union, Any
from datetime import datetime
from bson import ObjectId

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
    id: str
    conversation_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ConversationBase(BaseModel):
    title: Optional[str] = None
    context: Optional[str] = "consultant"
    bot_response_count: int = 0
    booking_status: str = "ongoing"

class ConversationCreate(ConversationBase):
    user_id: Optional[str] = None
    
    @field_validator('user_id', mode='before')
    @classmethod
    def validate_user_id(cls, v):
        if v is None:
            return None
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class ConversationUpdate(ConversationBase):
    booking_status: Optional[str] = None

class Conversation(ConversationBase):
    id: str
    user_id: Optional[str]
    bot_response_count: int = 0
    booking_status: str = "ongoing"
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class ConversationInDB(ConversationBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str] = None
    context: str
    bot_response_count: int
    booking_status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: Optional[int] = None  # For list views
    last_message: Optional[str] = None   # For list views

    model_config = ConfigDict(from_attributes=True)

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
    availability_id: str

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
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
    # AI Booking Response fields
    ai_is_schedule: Optional[bool] = None
    ai_booking_datetime: Optional[str] = None
    ai_booking_timezone: Optional[str] = None
    ai_booking_details: Optional[dict] = None 