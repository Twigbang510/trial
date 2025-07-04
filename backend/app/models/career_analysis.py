from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class CareerAnalysis(Base):
    __tablename__ = "career_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Test inputs
    mbti_type = Column(String(4), nullable=False)  # e.g., "ESFP"
    holland_scores = Column(JSON, nullable=False)  # {"realistic": 85, "investigative": 45, ...}
    
    # AI Analysis results
    personality_summary = Column(Text)
    holland_code = Column(String(6))  # e.g., "RIA"
    career_suggestions = Column(JSON)  # Array of career objects
    personality_traits = Column(JSON)  # Array of traits
    strengths = Column(JSON)  # Array of strengths
    growth_areas = Column(JSON)  # Array of growth areas
    
    # AI Generated content
    detailed_analysis = Column(Text)  # Full AI analysis text
    recommendations = Column(Text)  # AI recommendations
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="career_analyses") 