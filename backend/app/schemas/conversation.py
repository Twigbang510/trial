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

class ConversationCreate(ConversationBase):
    user_id: Optional[int] = None

class ConversationUpdate(BaseModel):
    title: Optional[str] = None

class Conversation(ConversationBase):
    id: int
    user_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ConversationList(BaseModel):
    id: int
    title: Optional[str]
    context: str
    created_at: datetime
    updated_at: Optional[datetime]
    message_count: int
    last_message: Optional[str]

    class Config:
        from_attributes = True 