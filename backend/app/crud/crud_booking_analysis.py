from typing import Optional
from sqlalchemy.orm import Session
from app.models.booking_analysis import BookingAnalysis
from app.crud.base import CRUDBase
from datetime import datetime

class CRUDBookingAnalysis(CRUDBase[BookingAnalysis, dict, dict]):
    """CRUD operations for BookingAnalysis model"""
    
    def create_analysis(
        self, 
        db: Session, 
        conversation_id: int,
        message_id: int,
        analysis_result: dict,
        processing_time_ms: Optional[int] = None
    ) -> BookingAnalysis:
        """Create a new booking analysis record"""
        
        db_analysis = BookingAnalysis(
            conversation_id=conversation_id,
            message_id=message_id,
            intent=analysis_result.get("intent", "O"),
            safety_score=analysis_result.get("safety_score", 50),
            is_rejection=analysis_result.get("is_rejection", False),
            is_confirmation=analysis_result.get("is_confirmation", False),
            input_slots=analysis_result.get("input_slots", []),
            time_range=analysis_result.get("time_range", []),
            extracted_date=analysis_result.get("date"),
            date_expressions=analysis_result.get("date_expressions", []),
            reasoning=analysis_result.get("reasoning"),
            processing_time_ms=processing_time_ms
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    
    def get_by_message_id(self, db: Session, message_id: int) -> Optional[BookingAnalysis]:
        """Get booking analysis by message ID"""
        return db.query(BookingAnalysis).filter(BookingAnalysis.message_id == message_id).first()
    
    def get_by_conversation_id(self, db: Session, conversation_id: int, limit: int = 50):
        """Get all booking analyses for a conversation"""
        return (
            db.query(BookingAnalysis)
            .filter(BookingAnalysis.conversation_id == conversation_id)
            .order_by(BookingAnalysis.created_at.desc())
            .limit(limit)
            .all()
        )
    
    def get_latest_analysis(self, db: Session, conversation_id: int) -> Optional[BookingAnalysis]:
        """Get the most recent booking analysis for a conversation"""
        return (
            db.query(BookingAnalysis)
            .filter(BookingAnalysis.conversation_id == conversation_id)
            .order_by(BookingAnalysis.created_at.desc())
            .first()
        )

# Create instance
booking_analysis = CRUDBookingAnalysis(BookingAnalysis) 
 