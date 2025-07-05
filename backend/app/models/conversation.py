from typing import Optional
from pydantic import Field, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class Conversation(BaseDocument):
    user_id: Optional[PyObjectId] = Field(None, description="User ID (nullable for anonymous users)")
    title: Optional[str] = Field(None, max_length=255, description="Auto-generated title from first message")
    context: str = Field(default="consultant", max_length=50, description="consultant, booking, etc.")
    bot_response_count: int = Field(default=0, description="Track number of bot responses")
    booking_status: str = Field(default="ongoing", max_length=20, description="ongoing, completed, abandoned")
    
    model_config = ConfigDict(
        collection_name="conversations",
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "title": "Conversation Title",
                "context": "consultant",
                "bot_response_count": 0,
                "booking_status": "ongoing"
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs"""
        data = self.model_dump()
        data["id"] = str(self.id)
        if self.user_id:
            data["user_id"] = str(self.user_id)
        return data 