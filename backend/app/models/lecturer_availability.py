from typing import Optional, List
from datetime import datetime, time, date, timedelta
from pydantic import Field, ConfigDict
from app.db.base import BaseDocument, PyObjectId

class LecturerAvailability(BaseDocument):
    """
    Store lecturer available time slots for appointment booking
    """
    lecturer_id: int = Field(..., description="Can link to user table later")
    lecturer_name: str = Field(..., max_length=100, description="Lecturer name")
    
    # Time slot information
    day_of_week: int = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    start_time: str = Field(..., description="08:00")
    end_time: str = Field(..., description="17:00")
    
    # Slot details
    slot_duration_minutes: int = Field(default=30, description="30 minutes per slot")
    max_slots_per_day: int = Field(default=10, description="Maximum bookings per day")
    
    # Availability status
    is_active: bool = Field(default=True, description="Is active")
    available_dates: List[str] = Field(default_factory=list, description="Specific dates when available")
    blocked_dates: List[str] = Field(default_factory=list, description="Specific dates when not available")
    
    # Metadata
    subject: Optional[str] = Field(None, max_length=100, description="Subject specialty")
    location: Optional[str] = Field(None, max_length=200, description="Meeting location")
    notes: Optional[str] = Field(None, description="Notes")
    
    model_config = ConfigDict(
        collection_name="lecturer_availability",
        json_schema_extra={
            "example": {
                "lecturer_id": 1,
                "lecturer_name": "Dr. John Doe",
                "day_of_week": 1,
                "start_time": "08:00",
                "end_time": "17:00",
                "slot_duration_minutes": 30,
                "max_slots_per_day": 10,
                "is_active": True,
                "available_dates": ["2024-01-15", "2024-01-16"],
                "blocked_dates": ["2024-01-20"],
                "subject": "Computer Science",
                "location": "Room 101",
                "notes": "Available for consultation"
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "lecturer_id": self.lecturer_id,
            "lecturer_name": self.lecturer_name,
            "day_of_week": self.day_of_week,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "slot_duration_minutes": self.slot_duration_minutes,
            "max_slots_per_day": self.max_slots_per_day,
            "is_active": self.is_active,
            "subject": self.subject,
            "location": self.location,
            "notes": self.notes
        }
    
    def get_available_slots(self, target_date=None) -> list:
        """Get list of available time slots for a specific date"""
        if not target_date:
            target_date = datetime.now().date()
        
        # Check if this day of week matches
        if target_date.weekday() != self.day_of_week:
            return []
        
        # Check if date is blocked
        date_str = target_date.strftime("%Y-%m-%d")
        if date_str in self.blocked_dates:
            return []
        
        # Generate time slots
        slots = []
        start_time = datetime.strptime(self.start_time, "%H:%M").time()
        end_time = datetime.strptime(self.end_time, "%H:%M").time()
        
        current_time = datetime.combine(target_date, start_time)
        end_datetime = datetime.combine(target_date, end_time)
        
        while current_time < end_datetime:
            slots.append({
                "time": current_time.strftime("%H:%M"),
                "datetime": current_time.isoformat(),
                "available": True  # Would check against bookings in real system
            })
            current_time += timedelta(minutes=self.slot_duration_minutes)
        
        return slots

class BookingSlot(BaseDocument):
    """
    Store actual bookings/reservations
    """
    lecturer_availability_id: PyObjectId = Field(..., description="Lecturer availability ID")
    user_id: Optional[int] = Field(None, description="User who booked")
    
    # Booking details
    booking_date: str = Field(..., description="YYYY-MM-DD")
    booking_time: str = Field(..., description="HH:MM")
    duration_minutes: int = Field(default=30, description="Duration in minutes")
    
    # Status
    status: str = Field(default="pending", max_length=20, description="pending, confirmed, cancelled")
    subject: Optional[str] = Field(None, max_length=200, description="Subject")
    notes: Optional[str] = Field(None, description="Notes")
    
    model_config = ConfigDict(
        collection_name="booking_slots",
        json_schema_extra={
            "example": {
                "lecturer_availability_id": "507f1f77bcf86cd799439011",
                "user_id": 1,
                "booking_date": "2024-01-15",
                "booking_time": "09:00",
                "duration_minutes": 30,
                "status": "pending",
                "subject": "Career Consultation",
                "notes": "First meeting"
            }
        }
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "lecturer_availability_id": str(self.lecturer_availability_id),
            "user_id": self.user_id,
            "booking_date": self.booking_date,
            "booking_time": self.booking_time,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "subject": self.subject,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 
 