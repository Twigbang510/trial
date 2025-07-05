from typing import List, Optional, Any
from pymongo.database import Database
from bson import ObjectId
from app.models.career_analysis import CareerAnalysis
from app.schemas.career_analysis import CareerAnalysisCreate, CareerAnalysisUpdate


class CRUDCareerAnalysis:
    def create_with_user(
        self, db: Database, *, obj_in: CareerAnalysisCreate, user_id: str
    ) -> CareerAnalysis:
        """Create career analysis for a specific user"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                raise ValueError("Invalid user_id")
            
        analysis_data = {
            "user_id": user_id,
            "mbti_type": obj_in.mbti_type,
            "holland_scores": obj_in.holland_scores.model_dump(),
            "personality_summary": None,
            "holland_code": None,
            "career_suggestions": [],
            "personality_traits": [],
            "strengths": [],
            "growth_areas": [],
            "detailed_analysis": None,
            "recommendations": None
        }
        
        collection = db.career_analyses
        result = collection.insert_one(analysis_data)
        
        # Get the created analysis
        created_analysis = collection.find_one({"_id": result.inserted_id})
        created_analysis["id"] = str(created_analysis["_id"])
        created_analysis["user_id"] = str(created_analysis["user_id"])
        return CareerAnalysis(**created_analysis)
    
    def get_by_user(
        self, db: Database, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[CareerAnalysis]:
        """Get all career analyses for a user, ordered by most recent"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return []
            
        collection = db.career_analyses
        cursor = collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
        analyses = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            analyses.append(CareerAnalysis(**doc))
        return analyses
    
    def get_latest_by_user(
        self, db: Database, *, user_id: str
    ) -> Optional[CareerAnalysis]:
        """Get the most recent career analysis for a user"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return None
            
        collection = db.career_analyses
        result = collection.find_one({"user_id": user_id}, sort=[("created_at", -1)])
        if result:
            result["id"] = str(result["_id"])
            result["user_id"] = str(result["user_id"])
            return CareerAnalysis(**result)
        return None
    
    def update_analysis_results(
        self, 
        db: Database, 
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
        update_data = {
            "personality_summary": personality_summary,
            "holland_code": holland_code,
            "career_suggestions": career_suggestions,
            "personality_traits": personality_traits,
            "strengths": strengths,
            "growth_areas": growth_areas,
            "detailed_analysis": detailed_analysis,
            "recommendations": recommendations
        }
        
        # Convert string id back to ObjectId for MongoDB query
        analysis_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.career_analyses
        collection.update_one(
            {"_id": analysis_id},
            {"$set": update_data}
        )
        
        # Get the updated analysis
        updated_analysis = collection.find_one({"_id": analysis_id})
        updated_analysis["id"] = str(updated_analysis["_id"])
        updated_analysis["user_id"] = str(updated_analysis["user_id"])
        return CareerAnalysis(**updated_analysis)
    
    def get(self, db: Database, id: Any) -> Optional[CareerAnalysis]:
        """Get career analysis by ID"""
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.career_analyses
        result = collection.find_one({"_id": id})
        if result:
            result["id"] = str(result["_id"])
            result["user_id"] = str(result["user_id"])
            return CareerAnalysis(**result)
        return None
    
    def update(self, db: Database, *, db_obj: CareerAnalysis, obj_in: CareerAnalysisUpdate) -> CareerAnalysis:
        """Update career analysis"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Convert string id back to ObjectId for MongoDB query
        analysis_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.career_analyses
        collection.update_one(
            {"_id": analysis_id},
            {"$set": update_data}
        )
        
        # Get the updated analysis
        updated_analysis = collection.find_one({"_id": analysis_id})
        updated_analysis["id"] = str(updated_analysis["_id"])
        updated_analysis["user_id"] = str(updated_analysis["user_id"])
        return CareerAnalysis(**updated_analysis)
    
    def delete(self, db: Database, *, id: Any) -> Optional[CareerAnalysis]:
        """Delete career analysis"""
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = db.career_analyses
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            doc["user_id"] = str(doc["user_id"])
            return CareerAnalysis(**doc)
        return None


career_analysis = CRUDCareerAnalysis() 