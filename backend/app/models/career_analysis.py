from typing import Optional, Dict, List, Any
from pydantic import Field, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class CareerAnalysis(BaseDocument):
    user_id: PyObjectId = Field(..., description="User ID")
    
    # Test inputs
    mbti_type: str = Field(..., max_length=4, description="e.g., 'ESFP'")
    holland_scores: Dict[str, int] = Field(..., description='{"realistic": 85, "investigative": 45, ...}')
    
    # AI Analysis results
    personality_summary: Optional[str] = Field(None, description="Personality summary")
    holland_code: Optional[str] = Field(None, max_length=6, description="e.g., 'RIA'")
    career_suggestions: Optional[List[Dict[str, Any]]] = Field(None, description="Array of career objects")
    personality_traits: Optional[List[str]] = Field(None, description="Array of traits")
    strengths: Optional[List[str]] = Field(None, description="Array of strengths")
    growth_areas: Optional[List[str]] = Field(None, description="Array of growth areas")
    
    # AI Generated content
    detailed_analysis: Optional[str] = Field(None, description="Full AI analysis text")
    recommendations: Optional[str] = Field(None, description="AI recommendations")
    
    model_config = ConfigDict(
        collection_name="career_analyses",
        json_schema_extra={
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "mbti_type": "ESFP",
                "holland_scores": {"realistic": 85, "investigative": 45},
                "personality_summary": "You are an outgoing person...",
                "holland_code": "RIA",
                "career_suggestions": [{"title": "Engineer", "description": "..."}],
                "personality_traits": ["Outgoing", "Practical"],
                "strengths": ["Communication", "Problem-solving"],
                "growth_areas": ["Patience", "Detail-orientation"],
                "detailed_analysis": "Detailed analysis text...",
                "recommendations": "Recommendations text..."
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary with string IDs"""
        data = self.model_dump()
        data["id"] = str(self.id)
        data["user_id"] = str(self.user_id)
        return data 