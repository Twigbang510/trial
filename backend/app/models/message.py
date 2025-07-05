from typing import Optional
from pydantic import Field, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class Message(BaseDocument):
    conversation_id: PyObjectId = Field(..., description="Conversation ID")
    content: str = Field(..., description="Message content")
    sender: str = Field(..., max_length=20, description="'user' or 'bot'")
    is_appropriate: bool = Field(default=True, description="For context control")
    
    model_config = ConfigDict(
        collection_name="messages",
        json_schema_extra={
            "example": {
                "conversation_id": "507f1f77bcf86cd799439011",
                "content": "Hello, how can I help you?",
                "sender": "bot",
                "is_appropriate": True
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs"""
        data = self.model_dump()
        data["id"] = str(self.id)
        data["conversation_id"] = str(self.conversation_id)
        return data 