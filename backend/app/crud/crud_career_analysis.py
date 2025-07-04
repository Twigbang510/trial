from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.crud.base import CRUDBase
from app.models.career_analysis import CareerAnalysis
from app.schemas.career_analysis import CareerAnalysisCreate, CareerAnalysisUpdate


class CRUDCareerAnalysis(CRUDBase[CareerAnalysis, CareerAnalysisCreate, CareerAnalysisUpdate]):
    def create_with_user(
        self, db: Session, *, obj_in: CareerAnalysisCreate, user_id: int
    ) -> CareerAnalysis:
        """Create career analysis for a specific user"""
        obj_in_data = obj_in.dict()
        obj_in_data["user_id"] = user_id
        obj_in_data["holland_scores"] = obj_in.holland_scores.dict()
        
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[CareerAnalysis]:
        """Get all career analyses for a user, ordered by most recent"""
        return (
            db.query(self.model)
            .filter(CareerAnalysis.user_id == user_id)
            .order_by(desc(CareerAnalysis.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_latest_by_user(
        self, db: Session, *, user_id: int
    ) -> Optional[CareerAnalysis]:
        """Get the most recent career analysis for a user"""
        return (
            db.query(self.model)
            .filter(CareerAnalysis.user_id == user_id)
            .order_by(desc(CareerAnalysis.created_at))
            .first()
        )
    
    def update_analysis_results(
        self, 
        db: Session, 
        *, 
        db_obj: CareerAnalysis,
        personality_summary: str,
        holland_code: str,
        career_suggestions: List[dict],
        personality_traits: List[str],
        strengths: List[str],
        growth_areas: List[str],
        detailed_analysis: str,
        recommendations: str
    ) -> CareerAnalysis:
        """Update career analysis with AI-generated results"""
        db_obj.personality_summary = personality_summary
        db_obj.holland_code = holland_code
        db_obj.career_suggestions = career_suggestions
        db_obj.personality_traits = personality_traits
        db_obj.strengths = strengths
        db_obj.growth_areas = growth_areas
        db_obj.detailed_analysis = detailed_analysis
        db_obj.recommendations = recommendations
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


career_analysis = CRUDCareerAnalysis(CareerAnalysis) 