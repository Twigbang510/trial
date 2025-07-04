from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any
from app.models.lecturer_availability import LecturerAvailability, BookingSlot
from app.crud.base import CRUDBase

class CRUDLecturerAvailability(CRUDBase[LecturerAvailability, Dict[str, Any], Dict[str, Any]]):
    """
    CRUD operations for lecturer availability
    """
    
    def find_matching_slots(
        self, 
        db: Session, 
        requested_times: List[str], 
        target_date: date,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find exact matching time slots for requested times
        """
        try:
            # Convert target_date to weekday (0=Monday, 6=Sunday)
            weekday = target_date.weekday()
            
            # Get all available lecturers for this day
            available_lecturers = db.query(LecturerAvailability).filter(
                and_(
                    LecturerAvailability.day_of_week == weekday,
                    LecturerAvailability.is_active == True
                )
            ).all()
            
            matching_slots = []
            
            for requested_time_str in requested_times:
                try:
                    # Parse time from string (e.g. "08:30", "14:15") 
                    if ":" in requested_time_str:
                        hour, minute = map(int, requested_time_str.split(":"))
                        requested_time = time(hour, minute)
                    else:
                        continue
                        
                    for lecturer in available_lecturers:
                        # Check if date is blocked for this lecturer
                        date_str = target_date.strftime("%Y-%m-%d")
                        if date_str in (lecturer.blocked_dates or []):
                            continue
                            
                        # Check if requested time falls within lecturer's available hours
                        if lecturer.start_time <= requested_time <= lecturer.end_time:
                            # Check if this time slot is not already booked
                            existing_booking = db.query(BookingSlot).filter(
                                and_(
                                    BookingSlot.lecturer_availability_id == lecturer.id,
                                    BookingSlot.booking_date == target_date,
                                    BookingSlot.booking_time == requested_time,
                                    BookingSlot.status.in_(["pending", "confirmed"])
                                )
                            ).first()
                            
                            if not existing_booking:
                                matching_slots.append({
                                    "availability_id": lecturer.id,
                                    "lecturer_name": lecturer.lecturer_name,
                                    "date": target_date.strftime("%Y-%m-%d"),
                                    "time": requested_time.strftime("%H:%M"),
                                    "subject": lecturer.subject or "General Consultation",
                                    "location": lecturer.location or "Office",
                                    "duration_minutes": lecturer.slot_duration_minutes or 30
                                })
                                
                except Exception as e:
                    continue
                    
            return matching_slots[:limit]
            
        except Exception as e:
            print(f"Error finding matching slots: {e}")
            return []
    
    def find_alternative_slots(
        self, 
        db: Session, 
        time_range: Optional[List[str]], 
        target_date: date,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find alternative time slots when exact matches aren't found
        """
        try:
            # Convert target_date to weekday
            weekday = target_date.weekday()
            
            # Get all available lecturers for this day
            available_lecturers = db.query(LecturerAvailability).filter(
                and_(
                    LecturerAvailability.day_of_week == weekday,
                    LecturerAvailability.is_active == True
                )
            ).all()
            
            alternative_slots = []
            
            for lecturer in available_lecturers:
                # Generate available time slots for this lecturer
                slots = self._generate_available_slots(db, lecturer, target_date)
                alternative_slots.extend(slots)
            
            # Sort by time and return limited results
            alternative_slots.sort(key=lambda x: x["time"])
            return alternative_slots[:limit]
            
        except Exception as e:
            print(f"Error finding alternative slots: {e}")
            return []
    
    def find_alternative_slots_in_range(
        self, 
        db: Session, 
        time_range: List[str], 
        target_date: date,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find alternative time slots within a specific time range
        """
        try:
            # Parse time range
            if not time_range or len(time_range) != 2:
                return []
            
            start_time_str, end_time_str = time_range
            if ":" not in start_time_str or ":" not in end_time_str:
                return []
                
            start_hour, start_min = map(int, start_time_str.split(":"))
            end_hour, end_min = map(int, end_time_str.split(":"))
            start_time = time(start_hour, start_min)
            end_time = time(end_hour, end_min)
            
            # Convert target_date to weekday
            weekday = target_date.weekday()
            
            # Get all available lecturers for this day
            available_lecturers = db.query(LecturerAvailability).filter(
                and_(
                    LecturerAvailability.day_of_week == weekday,
                    LecturerAvailability.is_active == True,
                    LecturerAvailability.start_time <= start_time,
                    LecturerAvailability.end_time >= end_time
                )
            ).all()
            
            alternative_slots = []
            
            for lecturer in available_lecturers:
                # Generate available time slots for this lecturer within range
                slots = self._generate_available_slots_in_range(db, lecturer, target_date, start_time, end_time)
                alternative_slots.extend(slots)
            
            # Sort by time and return limited results
            alternative_slots.sort(key=lambda x: x["time"])
            return alternative_slots[:limit]
            
        except Exception as e:
            print(f"Error finding alternative slots in range: {e}")
            return []
    
    def _generate_available_slots(
        self, 
        db: Session, 
        lecturer: LecturerAvailability, 
        target_date: date
    ) -> List[Dict[str, Any]]:
        """
        Generate all available time slots for a lecturer on a specific date
        """
        slots = []
        
        try:
            # Check if date is blocked for this lecturer
            date_str = target_date.strftime("%Y-%m-%d")
            if date_str in (lecturer.blocked_dates or []):
                return []
            
            # Start from lecturer's start time
            current_time = lecturer.start_time
            slot_duration = timedelta(minutes=lecturer.slot_duration_minutes or 30)
            
            while current_time < lecturer.end_time:
                # Check if this slot is already booked
                existing_booking = db.query(BookingSlot).filter(
                    and_(
                        BookingSlot.lecturer_availability_id == lecturer.id,
                        BookingSlot.booking_date == target_date,
                        BookingSlot.booking_time == current_time,
                        BookingSlot.status.in_(["pending", "confirmed"])
                    )
                ).first()
                
                if not existing_booking:
                    slots.append({
                        "availability_id": lecturer.id,
                        "lecturer_name": lecturer.lecturer_name,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "time": current_time.strftime("%H:%M"),
                        "subject": lecturer.subject or "General Consultation",
                        "location": lecturer.location or "Office",
                        "duration_minutes": lecturer.slot_duration_minutes or 30
                    })
                
                # Move to next slot
                current_datetime = datetime.combine(target_date, current_time)
                next_datetime = current_datetime + slot_duration
                current_time = next_datetime.time()
                
        except Exception as e:
            print(f"Error generating slots for lecturer {lecturer.id}: {e}")
            
        return slots
    
    def _generate_available_slots_in_range(
        self, 
        db: Session, 
        lecturer: LecturerAvailability, 
        target_date: date,
        start_time: time,
        end_time: time
    ) -> List[Dict[str, Any]]:
        """
        Generate available time slots for a lecturer within a specific time range
        """
        slots = []
        
        try:
            # Check if date is blocked for this lecturer
            date_str = target_date.strftime("%Y-%m-%d")
            if date_str in (lecturer.blocked_dates or []):
                return []
            
            # Use the more restrictive start/end time
            actual_start = max(lecturer.start_time, start_time)
            actual_end = min(lecturer.end_time, end_time)
            
            if actual_start >= actual_end:
                return []
            
            current_time = actual_start
            slot_duration = timedelta(minutes=lecturer.slot_duration_minutes or 30)
            
            while current_time < actual_end:
                # Check if this slot is already booked
                existing_booking = db.query(BookingSlot).filter(
                    and_(
                        BookingSlot.lecturer_availability_id == lecturer.id,
                        BookingSlot.booking_date == target_date,
                        BookingSlot.booking_time == current_time,
                        BookingSlot.status.in_(["pending", "confirmed"])
                    )
                ).first()
                
                if not existing_booking:
                    slots.append({
                        "availability_id": lecturer.id,
                        "lecturer_name": lecturer.lecturer_name,
                        "date": target_date.strftime("%Y-%m-%d"),
                        "time": current_time.strftime("%H:%M"),
                        "subject": lecturer.subject or "General Consultation",
                        "location": lecturer.location or "Office",
                        "duration_minutes": lecturer.slot_duration_minutes or 30
                    })
                
                # Move to next slot
                current_datetime = datetime.combine(target_date, current_time)
                next_datetime = current_datetime + slot_duration
                current_time = next_datetime.time()
                
        except Exception as e:
            print(f"Error generating slots in range for lecturer {lecturer.id}: {e}")
            
        return slots
    
    def create_booking_slot(
        self, 
        db: Session,
        availability_id: int,
        user_id: Optional[int],
        booking_date: str,  # "2025-01-27"
        booking_time: str,  # "08:30"
        subject: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[BookingSlot]:
        """
        Create a new booking slot
        """
        try:
            # Parse date and time
            if isinstance(booking_date, str):
                booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
            else:
                booking_date_obj = booking_date
                
            if isinstance(booking_time, str):
                if ":" in booking_time:
                    hour, minute = map(int, booking_time.split(":"))
                    booking_time_obj = time(hour, minute)
                else:
                    return None
            else:
                booking_time_obj = booking_time
            
            # Check if slot is still available
            existing_booking = db.query(BookingSlot).filter(
                and_(
                    BookingSlot.lecturer_availability_id == availability_id,
                    BookingSlot.booking_date == booking_date_obj,
                    BookingSlot.booking_time == booking_time_obj,
                    BookingSlot.status.in_(["pending", "confirmed"])
                )
            ).first()
            
            if existing_booking:
                print(f"Slot already booked: {booking_date_obj} {booking_time_obj}")
                return None
            
            # Create new booking
            booking_slot = BookingSlot(
                lecturer_availability_id=availability_id,
                user_id=user_id,
                booking_date=booking_date_obj,
                booking_time=booking_time_obj,
                status="confirmed",  # Directly confirm for now
                subject=subject,
                notes=notes
            )
            
            db.add(booking_slot)
            
            # Update lecturer's blocked_dates if this is the first booking for this date
            self._update_blocked_dates_if_needed(db, availability_id, booking_date_obj)
            
            db.commit()
            db.refresh(booking_slot)
            
            print(f"Created booking slot: ID={booking_slot.id}")
            return booking_slot
            
        except Exception as e:
            print(f"Error creating booking slot: {e}")
            db.rollback()
            return None
    
    def _update_blocked_dates_if_needed(
        self, 
        db: Session, 
        availability_id: int, 
        booking_date: date
    ) -> None:
        """
        Update lecturer's blocked_dates if this date should be marked as blocked
        (e.g., when lecturer reaches max slots per day)
        """
        try:
            lecturer = db.query(LecturerAvailability).filter(
                LecturerAvailability.id == availability_id
            ).first()
            
            if not lecturer:
                return
            
            # Count total bookings for this date
            total_bookings = db.query(BookingSlot).filter(
                and_(
                    BookingSlot.lecturer_availability_id == availability_id,
                    BookingSlot.booking_date == booking_date,
                    BookingSlot.status.in_(["pending", "confirmed"])
                )
            ).count()
            
            # If reached max slots, add to blocked_dates
            if total_bookings >= (lecturer.max_slots_per_day or 10):
                date_str = booking_date.strftime("%Y-%m-%d")
                blocked_dates = lecturer.blocked_dates or []
                
                if date_str not in blocked_dates:
                    blocked_dates.append(date_str)
                    lecturer.blocked_dates = blocked_dates
                    print(f"Added {date_str} to blocked_dates for lecturer {lecturer.id} (reached max slots: {total_bookings})")
            
        except Exception as e:
            print(f"Error updating blocked_dates: {e}")

    def get_user_bookings(
        self, 
        db: Session, 
        user_id: int,
        status_filter: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all bookings for a specific user with lecturer details
        """
        try:
            # Default status filter includes active bookings
            if status_filter is None:
                status_filter = ["pending", "confirmed"]
            
            # Query bookings with lecturer availability details
            bookings = db.query(BookingSlot, LecturerAvailability).join(
                LecturerAvailability,
                BookingSlot.lecturer_availability_id == LecturerAvailability.id
            ).filter(
                and_(
                    BookingSlot.user_id == user_id,
                    BookingSlot.status.in_(status_filter)
                )
            ).order_by(
                BookingSlot.booking_date.desc(),
                BookingSlot.booking_time.desc()
            ).limit(limit).all()
            
            result = []
            for booking_slot, lecturer_availability in bookings:
                result.append({
                    "id": booking_slot.id,
                    "booking_date": booking_slot.booking_date.strftime("%Y-%m-%d"),
                    "booking_time": booking_slot.booking_time.strftime("%H:%M"),
                    "duration_minutes": booking_slot.duration_minutes,
                    "status": booking_slot.status,
                    "subject": booking_slot.subject,
                    "notes": booking_slot.notes,
                    "created_at": booking_slot.created_at.isoformat() if booking_slot.created_at else None,
                    "lecturer": {
                        "id": lecturer_availability.id,
                        "name": lecturer_availability.lecturer_name,
                        "subject": lecturer_availability.subject,
                        "location": lecturer_availability.location,
                        "notes": lecturer_availability.notes
                    }
                })
            
            return result
            
        except Exception as e:
            print(f"Error getting user bookings: {e}")
            return []

# Create global instance
lecturer_availability = CRUDLecturerAvailability(LecturerAvailability) 