from typing import Optional, List
from pydantic import Field, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class BookingAnalysis(BaseDocument):
    """
    Store booking analysis results for each message
    Tracks intent classification and time extraction
    """
    conversation_id: PyObjectId = Field(..., description="Conversation ID")
    message_id: PyObjectId = Field(..., description="Message ID")
    
    # Intent Classification Results
    intent: str = Field(..., max_length=5, description="A, C, O")
    safety_score: int = Field(..., ge=1, le=99, description="1-99")
    is_rejection: bool = Field(default=False, description="Is rejection")
    is_confirmation: bool = Field(default=False, description="Is confirmation")
    
    # Time Extraction Results  
    input_slots: List[str] = Field(default_factory=list, description="['08:15', '14:00']")
    time_range: List[str] = Field(default_factory=list, description="['08:00', '10:00']")
    extracted_date: Optional[str] = Field(None, max_length=20, description="YYYY-MM-DD")
    date_expressions: List[str] = Field(default_factory=list, description="['today', 'tomorrow']")
    
    # Analysis Metadata
    reasoning: Optional[str] = Field(None, description="Analysis reasoning")
    analysis_version: str = Field(default="1.0", max_length=10, description="Track analysis version")
    processing_time_ms: Optional[int] = Field(None, description="Performance tracking")
    
    model_config = ConfigDict(
        collection_name="booking_analyses",
        json_schema_extra={
            "example": {
                "conversation_id": "507f1f77bcf86cd799439011",
                "message_id": "507f1f77bcf86cd799439012",
                "intent": "A",
                "safety_score": 85,
                "is_rejection": False,
                "is_confirmation": True,
                "input_slots": ["08:15", "14:00"],
                "time_range": ["08:00", "10:00"],
                "extracted_date": "2024-01-15",
                "date_expressions": ["today", "tomorrow"],
                "reasoning": "User confirmed booking time",
                "analysis_version": "1.0",
                "processing_time_ms": 150
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "conversation_id": str(self.conversation_id),
            "message_id": str(self.message_id),
            "intent": self.intent,
            "safety_score": self.safety_score,
            "is_rejection": self.is_rejection,
            "is_confirmation": self.is_confirmation,
            "input_slots": self.input_slots,
            "time_range": self.time_range,
            "date": self.extracted_date,
            "date_expressions": self.date_expressions,
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 
 