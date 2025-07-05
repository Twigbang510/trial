from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class HollandScores(BaseModel):
    realistic: int = Field(..., ge=0, le=100)
    investigative: int = Field(..., ge=0, le=100)
    artistic: int = Field(..., ge=0, le=100)
    social: int = Field(..., ge=0, le=100)
    enterprising: int = Field(..., ge=0, le=100)
    conventional: int = Field(..., ge=0, le=100)


class CareerSuggestion(BaseModel):
    title: str
    description: str
    match_percentage: int = Field(..., ge=0, le=100)
    required_skills: List[str]
    universities: List[str]
    industry: Optional[str] = None
    salary_range: Optional[str] = None


class CareerAnalysisCreate(BaseModel):
    mbti_type: str = Field(..., pattern="^[EI][SN][TF][JP]$")
    holland_scores: HollandScores


class CareerAnalysisResponse(BaseModel):
    id: str
    mbti_type: str
    holland_scores: Dict[str, int]
    holland_code: Optional[str]
    personality_summary: Optional[str]
    personality_traits: Optional[List[str]]
    strengths: Optional[List[str]]
    growth_areas: Optional[List[str]]
    career_suggestions: Optional[List[CareerSuggestion]]
    detailed_analysis: Optional[str]
    recommendations: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CareerAnalysisUpdate(BaseModel):
    mbti_type: Optional[str] = Field(None, pattern="^[EI][SN][TF][JP]$")
    holland_scores: Optional[HollandScores]


class CareerChatContext(BaseModel):
    """Context for career-related chat interactions"""
    analysis_id: str
    user_question: str
    focus_area: Optional[str] = None  # "careers", "education", "skills", etc. 