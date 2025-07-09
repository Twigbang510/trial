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
            # For AI-generated bookings, create a simple booking record without availability_id
            if availability_id == "ai_generated":
                return BookingService._create_ai_booking_slot(
                    db=db,
                    user=user,
                    booking_date=booking_date,
                    booking_time=booking_time,
                    subject=subject
                )
            else:
                # Use existing lecturer availability system
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
    def _create_ai_booking_slot(
        db: Database,
        user: Optional[User],
        booking_date: str,
        booking_time: str,
        subject: str
    ) -> bool:
        """Create a simple booking slot for AI-generated bookings"""
        try:
            from bson import ObjectId
            from datetime import datetime
            
            collection = db.ai_bookings  # Use a separate collection for AI bookings
            
            booking_data = {
                "user_id": ObjectId(str(getattr(user, 'id'))) if user else None,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "duration_minutes": 30,
                "status": "confirmed",
                "subject": subject,
                "lecturer_name": "Career Advisor",
                "location": "Online Meeting",
                "notes": f"AI-generated booking confirmed via chat at {datetime.now().isoformat()}",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = collection.insert_one(booking_data)
            return bool(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to create AI booking slot: {e}")
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
        message = "Unable to Complete Booking\n\n"
        message += "This time slot may have been taken by another student. "
        message += "Please try selecting a different time slot.\n\n"
        message += "Tip: Popular time slots fill up quickly. Consider booking alternative times for better availability."
        return message

    @staticmethod
    def process_ai_booking_response(
        db: Database,
        ai_response: dict,
        conversation_id: str,
        user: Optional[User]
    ) -> dict:
        """Process AI booking response and create booking"""
        try:
            logger.info(f"Processing AI booking response: {ai_response}")
            
            # Extract booking details from AI response
            datetime_str = ai_response.get("datetime", "")
            timezone = ai_response.get("timezone", "Indochina Timezone")
            
            # Parse datetime string (format: "1900-01-01 08:00:00, 2025-07-10 00:00:00")
            booking_details = BookingService._parse_ai_datetime(datetime_str)
            
            if not booking_details:
                logger.error(f"Failed to parse AI datetime: {datetime_str}")
                return {
                    "success": False,
                    "message": "Unable to process booking time. Please try again.",
                    "email_sent": False,
                    "booking_status": "ongoing"
                }
            
            # Create booking slot
            booking_success = BookingService.create_booking_slot(
                db=db,
                availability_id=booking_details.get("availability_id", "ai_generated"),
                user=user,
                booking_date=booking_details["date"],
                booking_time=booking_details["time"],
                subject=booking_details.get("subject", "Career Consultation")
            )
            
            if booking_success:
                # Complete conversation
                BookingService.complete_conversation(db, conversation_id)
                
                # Send confirmation email
                email_sent = BookingService.send_booking_confirmation_email(user, booking_details)
                
                # Generate success message
                success_message = BookingService.generate_success_message(booking_details, email_sent)
                
                return {
                    "success": True,
                    "message": success_message,
                    "email_sent": email_sent,
                    "booking_status": "complete",
                    "booking_details": booking_details
                }
            else:
                failure_message = BookingService.generate_failure_message()
                return {
                    "success": False,
                    "message": failure_message,
                    "email_sent": False,
                    "booking_status": "ongoing"
                }
                
        except Exception as e:
            logger.error(f"Error processing AI booking response: {e}")
            return {
                "success": False,
                "message": "An error occurred while processing your booking. Please try again.",
                "email_sent": False,
                "booking_status": "ongoing"
            }
    
    @staticmethod
    def _parse_ai_datetime(datetime_str: str) -> Optional[Dict[str, Any]]:
        """Parse datetime string from AI response"""
        try:
            # Handle format: "16:30:00, 2025-07-10" (time, date)
            if "," in datetime_str:
                # Split by comma and strip whitespace
                parts = [part.strip() for part in datetime_str.split(",")]
                
                if len(parts) == 2:
                    time_part = parts[0]  # "16:30:00"
                    date_part = parts[1]  # "2025-07-10"
                    
                    # Parse time (HH:MM:SS or HH:MM)
                    if ":" in time_part:
                        time_components = time_part.split(":")
                        if len(time_components) >= 2:
                            hour = int(time_components[0])
                            minute = int(time_components[1])
                            booking_time = f"{hour:02d}:{minute:02d}"
                        else:
                            logger.error(f"Invalid time format: {time_part}")
                            return None
                    else:
                        logger.error(f"Invalid time format: {time_part}")
                        return None
                    
                    # Parse date (YYYY-MM-DD)
                    try:
                        from datetime import datetime
                        parsed_date = datetime.strptime(date_part, "%Y-%m-%d")
                        booking_date = parsed_date.strftime("%Y-%m-%d")
                    except ValueError:
                        logger.error(f"Invalid date format: {date_part}")
                        return None
                    
                    return {
                        "date": booking_date,
                        "time": booking_time,
                        "lecturer_name": "Career Advisor",  # Default lecturer
                        "subject": "Career Consultation",
                        "location": "Online Meeting",
                        "duration_minutes": 30,
                        "availability_id": "ai_generated"
                    }
            
            # Handle other datetime formats if needed
            logger.error(f"Unsupported datetime format: {datetime_str}")
            return None
            
        except Exception as e:
            logger.error(f"Error parsing AI datetime: {e}")
            return None 