from typing import Optional, Any
from pymongo.database import Database
from bson import ObjectId
from app.models.booking_analysis import BookingAnalysis
from datetime import datetime

class CRUDBookingAnalysis:
    """CRUD operations for BookingAnalysis model"""
    
    def create_analysis(
        self, 
        db: Database, 
        conversation_id: Any,
        message_id: Any,
        analysis_result: dict,
        processing_time_ms: Optional[int] = None
    ) -> BookingAnalysis:
        """Create a new booking analysis record"""
        
        if isinstance(conversation_id, str):
            try:
                conversation_id = ObjectId(conversation_id)
            except:
                raise ValueError("Invalid conversation_id")
        if isinstance(message_id, str):
            try:
                message_id = ObjectId(message_id)
            except:
                raise ValueError("Invalid message_id")
        
        # Ensure time_range is always a list
        time_range = analysis_result.get("time_range")
        if time_range is None:
            time_range = []
        elif not isinstance(time_range, list):
            time_range = [str(time_range)] if time_range else []
        
        analysis_data = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "intent": analysis_result.get("intent", "O"),
            "safety_score": analysis_result.get("safety_score", 50),
            "is_rejection": analysis_result.get("is_rejection", False),
            "is_confirmation": analysis_result.get("is_confirmation", False),
            "input_slots": analysis_result.get("input_slots", []),
            "time_range": time_range,
            "extracted_date": analysis_result.get("date"),
            "date_expressions": analysis_result.get("date_expressions", []),
            "reasoning": analysis_result.get("reasoning"),
            "processing_time_ms": processing_time_ms
        }
        
        collection = db.booking_analyses
        result = collection.insert_one(analysis_data)
        
        # Get the created analysis
        created_analysis = collection.find_one({"_id": result.inserted_id})
        created_analysis["id"] = str(created_analysis["_id"])
        created_analysis["conversation_id"] = str(created_analysis["conversation_id"])
        created_analysis["message_id"] = str(created_analysis["message_id"])
        return BookingAnalysis(**created_analysis)
    
    def get_by_message_id(self, db: Database, message_id: Any) -> Optional[BookingAnalysis]:
        """Get booking analysis by message ID"""
        if isinstance(message_id, str):
            try:
                message_id = ObjectId(message_id)
            except:
                return None
        collection = db.booking_analyses
        result = collection.find_one({"message_id": message_id})
        if result:
            result["id"] = str(result["_id"])
            result["conversation_id"] = str(result["conversation_id"])
            result["message_id"] = str(result["message_id"])
            return BookingAnalysis(**result)
        return None
    
    def get_by_conversation_id(self, db: Database, conversation_id: Any, limit: int = 50):
        """Get all booking analyses for a conversation"""
        if isinstance(conversation_id, str):
            try:
                conversation_id = ObjectId(conversation_id)
            except:
                return []
        collection = db.booking_analyses
        cursor = collection.find({"conversation_id": conversation_id}).sort("created_at", -1).limit(limit)
        analyses = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["conversation_id"] = str(doc["conversation_id"])
            doc["message_id"] = str(doc["message_id"])
            analyses.append(BookingAnalysis(**doc))
        return analyses
    
    def get_latest_analysis(self, db: Database, conversation_id: Any) -> Optional[BookingAnalysis]:
        """Get the most recent booking analysis for a conversation"""
        if isinstance(conversation_id, str):
            try:
                conversation_id = ObjectId(conversation_id)
            except:
                return None
        collection = db.booking_analyses
        result = collection.find_one({"conversation_id": conversation_id}, sort=[("created_at", -1)])
        if result:
            result["id"] = str(result["_id"])
            result["conversation_id"] = str(result["conversation_id"])
            result["message_id"] = str(result["message_id"])
            return BookingAnalysis(**result)
        return None
    
    def get(self, db: Database, id: Any) -> Optional[BookingAnalysis]:
        """Get booking analysis by ID"""
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.booking_analyses
        result = collection.find_one({"_id": id})
        if result:
            result["id"] = str(result["_id"])
            result["conversation_id"] = str(result["conversation_id"])
            result["message_id"] = str(result["message_id"])
            return BookingAnalysis(**result)
        return None
    
    def update(self, db: Database, *, db_obj: BookingAnalysis, obj_in: dict) -> BookingAnalysis:
        """Update booking analysis"""
        # Convert string id back to ObjectId for MongoDB query
        analysis_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.booking_analyses
        collection.update_one(
            {"_id": analysis_id},
            {"$set": obj_in}
        )
        
        # Get the updated analysis
        updated_analysis = collection.find_one({"_id": analysis_id})
        updated_analysis["id"] = str(updated_analysis["_id"])
        updated_analysis["conversation_id"] = str(updated_analysis["conversation_id"])
        updated_analysis["message_id"] = str(updated_analysis["message_id"])
        return BookingAnalysis(**updated_analysis)
    
    def delete(self, db: Database, *, id: Any) -> Optional[BookingAnalysis]:
        """Delete booking analysis"""
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = db.booking_analyses
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            doc["conversation_id"] = str(doc["conversation_id"])
            doc["message_id"] = str(doc["message_id"])
            return BookingAnalysis(**doc)
        return None

# Create instance
booking_analysis = CRUDBookingAnalysis() 
 