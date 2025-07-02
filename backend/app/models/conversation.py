from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous users
    title = Column(String(255), nullable=True)  # Auto-generated title from first message
    context = Column(String(50), default="consultant")  # consultant, booking, etc.
    bot_response_count = Column(Integer, default=0)  # Track number of bot responses
    booking_status = Column(String(20), default="ongoing")  # ongoing, completed, abandoned
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    booking_analyses = relationship("BookingAnalysis", back_populates="conversation", cascade="all, delete-orphan") 