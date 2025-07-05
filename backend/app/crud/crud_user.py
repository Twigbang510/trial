# CRUD functions for user (template)
from pymongo.database import Database
from typing import Optional, Union, Dict, Any
from bson import ObjectId
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

class CRUDUser:
    def get(self, db: Database, id: Any) -> Optional[User]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.users
        result = collection.find_one({"_id": id})
        if result:
            # Convert ObjectId to string for the id field
            result["id"] = str(result["_id"])
            return User(**result)
        return None

    def get_by_email(self, db: Database, email: str) -> Optional[User]:
        collection = db.users
        result = collection.find_one({"email": email})
        if result:
            # Convert ObjectId to string for the id field
            result["id"] = str(result["_id"])
            return User(**result)
        return None

    def get_by_username(self, db: Database, *, username: str) -> Optional[User]:
        collection = db.users
        result = collection.find_one({"username": username})
        if result:
            # Convert ObjectId to string for the id field
            result["id"] = str(result["_id"])
            return User(**result)
        return None

    def get_list(self, db: Database, skip: int = 0, limit: int = 100):
        collection = db.users
        cursor = collection.find().skip(skip).limit(limit)
        users = []
        for doc in cursor:
            # Convert ObjectId to string for the id field
            doc["id"] = str(doc["_id"])
            users.append(User(**doc))
        return users

    def create(self, db: Database, *, obj_in: UserCreate) -> User:
        user_data = {
            "email": obj_in.email,
            "username": obj_in.username,
            "full_name": obj_in.full_name,
            "hashed_password": get_password_hash(obj_in.password),
            "is_active": True,
            "is_verified": False,
            "status": obj_in.status,
            "violation_count": 0
        }
        
        collection = db.users
        result = collection.insert_one(user_data)
        
        # Get the created user
        created_user = collection.find_one({"_id": result.inserted_id})
        created_user["id"] = str(created_user["_id"])
        return User(**created_user)

    def update(
        self, db: Database, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        # Convert string id back to ObjectId for MongoDB query
        user_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.users
        collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        # Get the updated user
        updated_user = collection.find_one({"_id": user_id})
        updated_user["id"] = str(updated_user["_id"])
        return User(**updated_user)

    def authenticate(self, db: Database, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return bool(user.is_active)

    def is_verified(self, user: User) -> bool:
        return bool(user.is_verified)
    
    def increment_violation(self, db: Database, *, user: User, violation_type: str = "WARNING") -> User:
        """
        Increment user's violation count and deactivate if threshold is reached
        
        Args:
            db: Database session
            user: User object
            violation_type: Type of violation ("WARNING" or "BLOCK")
            
        Returns:
            Updated user object
        """
        current_count = getattr(user, 'violation_count', 0) or 0
        new_count = current_count + 1
        
        update_data = {"violation_count": new_count}
        
        # Deactivate user if they have 5 or more violations
        if new_count >= 5:
            update_data["is_active"] = False
        
        # Convert string id back to ObjectId for MongoDB query
        user_id = ObjectId(user.id) if isinstance(user.id, str) else user.id
        
        collection = db.users
        collection.update_one(
            {"_id": user_id},
            {"$set": update_data}
        )
        
        # Get the updated user
        updated_user = collection.find_one({"_id": user_id})
        updated_user["id"] = str(updated_user["_id"])
        return User(**updated_user)
    
    def reset_violations(self, db: Database, *, user: User) -> User:
        """
        Reset user's violation count (admin function)
        
        Args:
            db: Database session
            user: User object
            
        Returns:
            Updated user object
        """
        # Convert string id back to ObjectId for MongoDB query
        user_id = ObjectId(user.id) if isinstance(user.id, str) else user.id
        
        collection = db.users
        collection.update_one(
            {"_id": user_id},
            {"$set": {"violation_count": 0, "is_active": True}}
        )
        
        # Get the updated user
        updated_user = collection.find_one({"_id": user_id})
        updated_user["id"] = str(updated_user["_id"])
        return User(**updated_user)

user_crud = CRUDUser() 