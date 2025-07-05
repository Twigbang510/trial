from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional, Any, Dict
from app.models.lecturer_availability import LecturerAvailability, BookingSlot
from datetime import datetime, date, timedelta

class CRUDLecturerAvailability:
    def create(self, db: Database, *, obj_in: Dict[str, Any]) -> LecturerAvailability:
        collection = db.lecturer_availability
        result = collection.insert_one(obj_in)
        
        # Get the created availability
        created_availability = collection.find_one({"_id": result.inserted_id})
        created_availability["id"] = str(created_availability["_id"])
        return LecturerAvailability(**created_availability)

    def get(self, db: Database, id: Any) -> Optional[LecturerAvailability]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.lecturer_availability
        result = collection.find_one({"_id": id})
        if result:
            result["id"] = str(result["_id"])
            return LecturerAvailability(**result)
        return None

    def get_list(self, db: Database, skip: int = 0, limit: int = 100) -> List[LecturerAvailability]:
        collection = db.lecturer_availability
        cursor = collection.find().skip(skip).limit(limit)
        availabilities = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            availabilities.append(LecturerAvailability(**doc))
        return availabilities

    def update(self, db: Database, *, db_obj: LecturerAvailability, obj_in: Dict[str, Any]) -> LecturerAvailability:
        # Convert string id back to ObjectId for MongoDB query
        availability_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.lecturer_availability
        collection.update_one(
            {"_id": availability_id},
            {"$set": obj_in}
        )
        
        # Get the updated availability
        updated_availability = collection.find_one({"_id": availability_id})
        updated_availability["id"] = str(updated_availability["_id"])
        return LecturerAvailability(**updated_availability)

    def delete(self, db: Database, *, id: Any) -> Optional[LecturerAvailability]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = db.lecturer_availability
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            return LecturerAvailability(**doc)
        return None

    def get_user_bookings(self, db: Database, user_id: Any, status_filter: Optional[List[str]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get bookings for a specific user"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return []
        
        collection = db.lecturer_availability
        query = {"user_id": user_id}
        
        if status_filter:
            query["status"] = {"$in": status_filter}
        
        cursor = collection.find(query).sort("created_at", -1).limit(limit)
        return list(cursor)

    def get_available_slots(self, db: Database, date: str) -> List[Dict[str, Any]]:
        """Get available booking slots for a specific date"""
        collection = db.lecturer_availability
        cursor = collection.find({
            "date": date,
            "status": "available"
        }).sort("start_time", 1)
        return list(cursor)

    def find_matching_slots(self, db: Database, user_slots: List[str], target_date: date) -> List[Dict[str, Any]]:
        """Find slots that match user's requested times"""
        collection = db.lecturer_availability
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Find slots for the target date
        slots = collection.find({
            "day_of_week": target_date.weekday(),
            "is_active": True
        })
        
        matching_slots = []
        for slot in slots:
            # Generate available times for this slot
            available_times = self._generate_slot_times(slot, date_str)
            
            # Check if any user requested times match
            for user_time in user_slots:
                if user_time in available_times:
                    matching_slots.append({
                        "lecturer_name": slot.get("lecturer_name", "Unknown"),
                        "date": date_str,
                        "time": user_time,
                        "subject": slot.get("subject", "General"),
                        "location": slot.get("location", "TBD"),
                        "duration_minutes": slot.get("slot_duration_minutes", 30),
                        "availability_id": str(slot["_id"])
                    })
        
        return matching_slots

    def find_alternative_slots(self, db: Database, user_slots: Optional[List[str]], target_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        """Find alternative slots when exact matches aren't available"""
        collection = db.lecturer_availability
        
        # Get all active slots for the target date
        slots = collection.find({
            "day_of_week": target_date.weekday(),
            "is_active": True
        }).limit(limit)
        
        alternative_slots = []
        for slot in slots:
            date_str = target_date.strftime("%Y-%m-%d")
            available_times = self._generate_slot_times(slot, date_str)
            
            # Take first few available times
            for time in available_times[:3]:
                alternative_slots.append({
                    "lecturer_name": slot.get("lecturer_name", "Unknown"),
                    "date": date_str,
                    "time": time,
                    "subject": slot.get("subject", "General"),
                    "location": slot.get("location", "TBD"),
                    "duration_minutes": slot.get("slot_duration_minutes", 30),
                    "availability_id": str(slot["_id"])
                })
        
        return alternative_slots[:limit]

    def find_alternative_slots_in_range(self, db: Database, user_range: List[str], target_date: date, limit: int = 5) -> List[Dict[str, Any]]:
        """Find alternative slots within user's time range"""
        collection = db.lecturer_availability
        
        if len(user_range) < 2:
            return self.find_alternative_slots(db, None, target_date, limit)
        
        start_time = user_range[0]
        end_time = user_range[1]
        
        # Get all active slots for the target date
        slots = collection.find({
            "day_of_week": target_date.weekday(),
            "is_active": True
        })
        
        alternative_slots = []
        for slot in slots:
            date_str = target_date.strftime("%Y-%m-%d")
            available_times = self._generate_slot_times(slot, date_str)
            
            # Filter times within user's range
            for time in available_times:
                if start_time <= time <= end_time:
                    alternative_slots.append({
                        "lecturer_name": slot.get("lecturer_name", "Unknown"),
                        "date": date_str,
                        "time": time,
                        "subject": slot.get("subject", "General"),
                        "location": slot.get("location", "TBD"),
                        "duration_minutes": slot.get("slot_duration_minutes", 30),
                        "availability_id": str(slot["_id"])
                    })
        
        return alternative_slots[:limit]

    def _generate_slot_times(self, slot: Dict[str, Any], date_str: str) -> List[str]:
        """Generate available time slots for a given availability"""
        try:
            start_time = datetime.strptime(slot.get("start_time", "08:00"), "%H:%M").time()
            end_time = datetime.strptime(slot.get("end_time", "17:00"), "%H:%M").time()
            duration = slot.get("slot_duration_minutes", 30)
            
            times = []
            current_time = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), start_time)
            end_datetime = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d").date(), end_time)
            
            while current_time < end_datetime:
                times.append(current_time.strftime("%H:%M"))
                current_time += timedelta(minutes=duration)
            
            return times
        except Exception:
            return ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]

    def create_booking_slot(self, db: Database, availability_id: str, user_id: Optional[str], booking_date: str, booking_time: str, subject: str, notes: str = "") -> Optional[Dict[str, Any]]:
        """Create a booking slot"""
        try:
            if isinstance(availability_id, str):
                availability_id = ObjectId(availability_id)
            if user_id and isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            collection = db.booking_slots
            
            booking_data = {
                "lecturer_availability_id": availability_id,
                "user_id": user_id,
                "booking_date": booking_date,
                "booking_time": booking_time,
                "duration_minutes": 30,
                "status": "pending",
                "subject": subject,
                "notes": notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = collection.insert_one(booking_data)
            created_booking = collection.find_one({"_id": result.inserted_id})
            if created_booking:
                # Convert all ObjectId fields to strings
                created_booking["id"] = str(created_booking["_id"])
                created_booking["lecturer_availability_id"] = str(created_booking["lecturer_availability_id"])
                if created_booking.get("user_id"):
                    created_booking["user_id"] = str(created_booking["user_id"])
                
                # Remove the original _id field to avoid confusion
                if "_id" in created_booking:
                    del created_booking["_id"]
            
            return created_booking
        except Exception as e:
            print(f"Error creating booking slot: {e}")
            return None

    def book_slot(self, db: Database, slot_id: Any, user_id: Any, booking_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Book a slot for a user"""
        if isinstance(slot_id, str):
            try:
                slot_id = ObjectId(slot_id)
            except:
                return None
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
        
        collection = db.lecturer_availability
        
        # Check if slot is still available
        slot = collection.find_one({"_id": slot_id, "status": "available"})
        if not slot:
            return None
        
        # Update slot with booking information
        booking_data["user_id"] = user_id
        booking_data["status"] = "booked"
        booking_data["booked_at"] = datetime.utcnow()
        
        collection.update_one(
            {"_id": slot_id},
            {"$set": booking_data}
        )
        
        # Get the updated slot
        updated_slot = collection.find_one({"_id": slot_id})
        if updated_slot:
            updated_slot["id"] = str(updated_slot["_id"])
            if updated_slot.get("user_id"):
                updated_slot["user_id"] = str(updated_slot["user_id"])
        return updated_slot

    def cancel_booking(self, db: Database, slot_id: Any, user_id: Any) -> Optional[Dict[str, Any]]:
        """Cancel a booking"""
        if isinstance(slot_id, str):
            try:
                slot_id = ObjectId(slot_id)
            except:
                return None
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
        
        collection = db.lecturer_availability
        
        # Check if slot belongs to user
        slot = collection.find_one({"_id": slot_id, "user_id": user_id})
        if not slot:
            return None
        
        # Reset slot to available
        collection.update_one(
            {"_id": slot_id},
            {"$set": {
                "status": "available",
                "user_id": None,
                "booked_at": None,
                "cancelled_at": datetime.utcnow()
            }}
        )
        
        # Get the updated slot
        updated_slot = collection.find_one({"_id": slot_id})
        if updated_slot:
            updated_slot["id"] = str(updated_slot["_id"])
        return updated_slot

lecturer_availability = CRUDLecturerAvailability() 