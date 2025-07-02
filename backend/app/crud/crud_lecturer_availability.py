from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict
from app.models.lecturer_availability import LecturerAvailability, BookingSlot

class LecturerAvailabilityCRUD:
    def get_by_id(self, db: Session, availability_id: int) -> Optional[LecturerAvailability]:
        return db.query(LecturerAvailability).filter(LecturerAvailability.id == availability_id).first()

    def get_all_active(self, db: Session) -> List[LecturerAvailability]:
        return db.query(LecturerAvailability).filter(LecturerAvailability.is_active == True).all()

    def find_matching_slots(
        self, db: Session, user_slots: List[str], target_date: Optional[date] = None
    ) -> List[Dict]:
        """
        Tìm các slot trùng khớp với thời gian user yêu cầu (user_slots: ['08:00', ...])
        """
        if not user_slots:
            return []
            
        # Default to next Monday if no target date
        if not target_date:
            today = datetime.now().date()
            days_ahead = 0 - today.weekday()  # Monday is 0
            if days_ahead <= 0:  # If today is Monday or past Monday, get next Monday
                days_ahead += 7
            target_date = today + timedelta(days_ahead)
            
        results = []
        availabilities = self.get_all_active(db)
        
        for avail in availabilities:
            slots = avail.get_available_slots(target_date)
            for slot in slots:
                if slot['time'] in user_slots and slot.get('available', True):
                    # Check if this slot is already booked
                    if not self._is_slot_booked(db, avail.id, target_date, slot['time']):
                        results.append({
                            'lecturer_name': avail.lecturer_name,
                            'date': target_date.strftime('%Y-%m-%d'),  # Use target_date directly
                            'time': slot['time'],
                            'subject': avail.subject or 'General Consultation',
                            'location': avail.location or 'TBD',
                            'duration_minutes': avail.slot_duration_minutes,
                            'availability_id': avail.id
                        })
        return results

    def find_alternative_slots(
        self, db: Session, user_range: List[str], target_date: Optional[date] = None, limit: int = 5
    ) -> List[Dict]:
        """
        Tìm các slot nằm trong khoảng thời gian user yêu cầu (user_range: ['08:00', '10:00'])
        """
        # Default to next Monday if no target date
        if not target_date:
            today = datetime.now().date()
            days_ahead = 0 - today.weekday()  # Monday is 0
            if days_ahead <= 0:  # If today is Monday or past Monday, get next Monday
                days_ahead += 7
            target_date = today + timedelta(days_ahead)
            
        results = []
        availabilities = self.get_all_active(db)
        
        for avail in availabilities:
            slots = avail.get_available_slots(target_date)
            for slot in slots:
                # If no range specified, show all available slots
                time_in_range = True
                if user_range and len(user_range) == 2:
                    time_in_range = user_range[0] <= slot['time'] <= user_range[1]
                
                if time_in_range and slot.get('available', True):
                    # Check if this slot is already booked
                    if not self._is_slot_booked(db, avail.id, target_date, slot['time']):
                        results.append({
                            'lecturer_name': avail.lecturer_name,
                            'date': target_date.strftime('%Y-%m-%d'),  # Use target_date directly
                            'time': slot['time'],
                            'subject': avail.subject or 'General Consultation',
                            'location': avail.location or 'TBD',
                            'duration_minutes': avail.slot_duration_minutes,
                            'availability_id': avail.id
                        })
                        if len(results) >= limit:
                            return results
        return results

    def _is_slot_booked(self, db: Session, availability_id: int, booking_date: Optional[date], booking_time: str) -> bool:
        """Check if a specific time slot is already booked"""
        try:
            if not booking_date:
                booking_date = datetime.now().date()
            
            # Parse time string to time object
            time_obj = datetime.strptime(booking_time, "%H:%M").time()
            
            # Check if booking exists for this slot
            existing_booking = db.query(BookingSlot).filter(
                and_(
                    BookingSlot.lecturer_availability_id == availability_id,
                    BookingSlot.booking_date == booking_date,
                    BookingSlot.booking_time == time_obj,
                    BookingSlot.status.in_(["pending", "confirmed"])  # Only check active bookings
                )
            ).first()
            
            return existing_booking is not None
        except Exception:
            return False

    def create_booking_slot(
        self, 
        db: Session, 
        availability_id: int, 
        user_id: Optional[int], 
        booking_date: str, 
        booking_time: str,
        subject: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[BookingSlot]:
        """
        Tạo booking slot mới khi user xác nhận
        """
        try:
            # Validate availability exists
            availability = self.get_by_id(db, availability_id)
            if not availability:
                return None
            
            # Parse date and time
            date_obj = datetime.strptime(booking_date, "%Y-%m-%d").date()
            time_obj = datetime.strptime(booking_time, "%H:%M").time()
            
            # Check if slot is already booked
            if self._is_slot_booked(db, availability_id, date_obj, booking_time):
                return None
            
            # Create new booking
            new_booking = BookingSlot(
                lecturer_availability_id=availability_id,
                user_id=user_id,
                booking_date=date_obj,
                booking_time=time_obj,
                duration_minutes=availability.slot_duration_minutes,
                status="confirmed",  # Directly confirmed since user explicitly confirmed
                subject=subject or availability.subject,
                notes=notes
            )
            
            db.add(new_booking)
            db.commit()
            db.refresh(new_booking)
            
            return new_booking
            
        except Exception as e:
            db.rollback()
            print(f"Error creating booking slot: {e}")
            return None

    def get_user_bookings(self, db: Session, user_id: int) -> List[BookingSlot]:
        """Get all bookings for a specific user"""
        return db.query(BookingSlot).filter(
            and_(
                BookingSlot.user_id == user_id,
                BookingSlot.status.in_(["pending", "confirmed"])
            )
        ).order_by(BookingSlot.booking_date.desc(), BookingSlot.booking_time.desc()).all()

lecturer_availability = LecturerAvailabilityCRUD() 