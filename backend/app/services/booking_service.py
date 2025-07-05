from typing import Optional, Dict, Any
from pymongo.database import Database
from fastapi import HTTPException
from datetime import datetime
from app.crud import lecturer_availability
from app.crud.crud_conversation import conversation
from app.schemas.conversation import ConversationUpdate
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class BookingService:
    """Service for booking-related business logic"""
    
    @staticmethod
    def create_booking_slot(
        db: Database,
        availability_id: str,
        user: Optional[User],
        booking_date: str,
        booking_time: str,
        subject: str
    ) -> bool:
        """Create a booking slot and return success status"""
        try:
            booking_slot = lecturer_availability.create_booking_slot(
                db=db,
                availability_id=availability_id,
                user_id=str(getattr(user, 'id')) if user else None,
                booking_date=booking_date,
                booking_time=booking_time,
                subject=subject,
                notes=f"Confirmed via chat at {datetime.now().isoformat()}"
            )
            return bool(booking_slot)
        except Exception as e:
            logger.error(f"Failed to create booking slot: {e}")
            return False
    
    @staticmethod
    def complete_conversation(db: Database, conv_id: str) -> None:
        """Mark conversation as complete"""
        conv = conversation.get(db, id=conv_id)
        if conv:
            conversation.update(
                db, 
                db_obj=conv, 
                obj_in=ConversationUpdate(booking_status="complete")
            )
    
    @staticmethod
    def send_booking_confirmation_email(user: Optional[User], booking_details: Dict[str, Any]) -> bool:
        """Send booking confirmation email if user has email"""
        if not user or not hasattr(user, 'email') or not user.email:
            return False
            
        try:
            from app.core.email import send_booking_confirmation_email
            return send_booking_confirmation_email(user.email, booking_details)
        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")
            return False
    
    @staticmethod
    def generate_success_message(booking_details: Dict[str, Any], email_sent: bool) -> str:
        """Generate booking success message"""
        message = "🎉 Booking Confirmed Successfully!\n\n"
        message += "📅 Your Appointment Details:\n"
        message += f"👨‍🏫 Lecturer: {booking_details['lecturer_name']}\n"
        message += f"📅 Date: {booking_details['date']}\n"
        message += f"⏰ Time: {booking_details['time']}\n"
        message += f"📚 Subject: {booking_details['subject']}\n"
        message += f"📍 Location: {booking_details['location']}\n"
        message += f"⏱️ Duration: {booking_details['duration_minutes']} minutes\n\n"
        
        if email_sent:
            message += "📧 Email Confirmation Sent! Check your inbox for detailed booking information.\n\n"
        else:
            message += "📧 Email confirmation will be sent shortly.\n\n"
            
        return message
    
    @staticmethod
    def generate_failure_message() -> str:
        """Generate booking failure message"""
        message = "❌ Unable to Complete Booking\n\n"
        message += "This time slot may have been taken by another student. "
        message += "Please try selecting a different time slot.\n\n"
        message += "💡 Tip: Popular time slots fill up quickly. Consider booking alternative times for better availability."
        return message 