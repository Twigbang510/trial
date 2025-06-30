from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str
    sender: str
    is_appropriate: Optional[bool] = True

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: Optional[str] = None
    context: str = "consultant"
    bot_response_count: int = 0
    booking_status: str = "ongoing"

class ConversationCreate(ConversationBase):
    user_id: Optional[int] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    context: Optional[str] = None
    bot_response_count: Optional[int] = None
    booking_status: Optional[str] = None

class ConversationInDB(ConversationBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Conversation(ConversationInDB):
    pass

# Response schemas for API
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