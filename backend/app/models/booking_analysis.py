from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class BookingAnalysis(Base):
    """
    Store booking analysis results for each message
    Tracks intent classification and time extraction
    """
    __tablename__ = "booking_analyses"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    
    # Intent Classification Results
    intent = Column(String(5), nullable=False)  # A, C, O
    safety_score = Column(Integer, nullable=False)  # 1-99
    is_rejection = Column(Boolean, default=False)
    is_confirmation = Column(Boolean, default=False)
    
    # Time Extraction Results  
    input_slots = Column(JSON, default=list)  # ["08:15", "14:00"]
    time_range = Column(JSON, default=list)   # ["08:00", "10:00"] 
    extracted_date = Column(String(20), nullable=True)  # YYYY-MM-DD
    date_expressions = Column(JSON, default=list)  # ["today", "tomorrow"]
    
    # Analysis Metadata
    reasoning = Column(Text, nullable=True)
    analysis_version = Column(String(10), default="1.0")  # Track analysis version
    processing_time_ms = Column(Integer, nullable=True)  # Performance tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="booking_analyses")
    message = relationship("Message", back_populates="booking_analysis")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "message_id": self.message_id,
            "intent": self.intent,
            "safety_score": self.safety_score,
            "is_rejection": self.is_rejection,
            "is_confirmation": self.is_confirmation,
            "input_slots": self.input_slots or [],
            "time_range": self.time_range or [],
            "date": self.extracted_date,
            "date_expressions": self.date_expressions or [],
            "reasoning": self.reasoning,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 
 