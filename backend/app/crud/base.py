from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from datetime import datetime
from bson import ObjectId
from pymongo.database import Database
from pymongo.collection import Collection
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.db.base import BaseDocument

ModelType = TypeVar("ModelType", bound=BaseDocument)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A Pydantic model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get_collection(self, db: Database) -> Collection:
        """Get MongoDB collection for this model"""
        collection_name = self.model.model_config.get("collection_name", "default")
        return db[collection_name]

    def get(self, db: Database, id: Any) -> Optional[ModelType]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = self.get_collection(db)
        result = collection.find_one({"_id": id})
        if result:
            # Convert ObjectId to string for the id field
            result["id"] = str(result["_id"])
            return self.model(**result)
        return None

    def get_multi(
        self, db: Database, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        collection = self.get_collection(db)
        cursor = collection.find().skip(skip).limit(limit)
        models = []
        for doc in cursor:
            # Convert ObjectId to string for the id field
            doc["id"] = str(doc["_id"])
            models.append(self.model(**doc))
        return models

    def create(self, db: Database, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["created_at"] = datetime.utcnow()
        obj_in_data["updated_at"] = datetime.utcnow()
        
        collection = self.get_collection(db)
        result = collection.insert_one(obj_in_data)
        
        # Get the created document
        created_doc = collection.find_one({"_id": result.inserted_id})
        created_doc["id"] = str(created_doc["_id"])
        return self.model(**created_doc)

    def update(
        self,
        db: Database,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Convert string id back to ObjectId for MongoDB query
        doc_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = self.get_collection(db)
        collection.update_one(
            {"_id": doc_id},
            {"$set": update_data}
        )
        
        # Get the updated document
        updated_doc = collection.find_one({"_id": doc_id})
        updated_doc["id"] = str(updated_doc["_id"])
        return self.model(**updated_doc)

    def remove(self, db: Database, *, id: Any) -> Optional[ModelType]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = self.get_collection(db)
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            return self.model(**doc)
        return None 
 