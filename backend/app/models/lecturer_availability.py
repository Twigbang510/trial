from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON, Time, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class LecturerAvailability(Base):
    """
    Store lecturer available time slots for appointment booking
    """
    __tablename__ = "lecturer_availability"

    id = Column(Integer, primary_key=True, index=True)
    lecturer_id = Column(Integer, nullable=False)  # Can link to user table later
    lecturer_name = Column(String(100), nullable=False)
    
    # Time slot information
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)      # 08:00
    end_time = Column(Time, nullable=False)        # 17:00
    
    # Slot details
    slot_duration_minutes = Column(Integer, default=30)  # 30 minutes per slot
    max_slots_per_day = Column(Integer, default=10)      # Maximum bookings per day
    
    # Availability status
    is_active = Column(Boolean, default=True)
    available_dates = Column(JSON, default=list)  # Specific dates when available
    blocked_dates = Column(JSON, default=list)    # Specific dates when not available
    
    # Metadata
    subject = Column(String(100), nullable=True)   # Subject specialty
    location = Column(String(200), nullable=True)  # Meeting location
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "lecturer_id": self.lecturer_id,
            "lecturer_name": self.lecturer_name,
            "day_of_week": self.day_of_week,
            "start_time": self.start_time.strftime("%H:%M") if self.start_time else None,
            "end_time": self.end_time.strftime("%H:%M") if self.end_time else None,
            "slot_duration_minutes": self.slot_duration_minutes,
            "max_slots_per_day": self.max_slots_per_day,
            "is_active": self.is_active,
            "subject": self.subject,
            "location": self.location,
            "notes": self.notes
        }
    
    def get_available_slots(self, target_date=None) -> list:
        """Get list of available time slots for a specific date"""
        from datetime import datetime, timedelta
        
        if not target_date:
            target_date = datetime.now().date()
        
        # Check if this day of week matches
        if target_date.weekday() != self.day_of_week:
            return []
        
        # Check if date is blocked
        date_str = target_date.strftime("%Y-%m-%d")
        if date_str in (self.blocked_dates or []):
            return []
        
        # Generate time slots
        slots = []
        current_time = datetime.combine(target_date, self.start_time)
        end_time = datetime.combine(target_date, self.end_time)
        
        while current_time < end_time:
            slots.append({
                "time": current_time.strftime("%H:%M"),
                "datetime": current_time.isoformat(),
                "available": True  # Would check against bookings in real system
            })
            current_time += timedelta(minutes=self.slot_duration_minutes)
        
        return slots

class BookingSlot(Base):
    """
    Store actual bookings/reservations
    """
    __tablename__ = "booking_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    lecturer_availability_id = Column(Integer, ForeignKey("lecturer_availability.id"), nullable=False)
    user_id = Column(Integer, nullable=True)  # User who booked
    
    # Booking details
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, cancelled
    subject = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lecturer_availability = relationship("LecturerAvailability", backref="bookings")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "lecturer_availability_id": self.lecturer_availability_id,
            "user_id": self.user_id,
            "booking_date": self.booking_date.strftime("%Y-%m-%d"),
            "booking_time": self.booking_time.strftime("%H:%M"),
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "subject": self.subject,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 
 