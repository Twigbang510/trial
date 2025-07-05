from pymongo.database import Database
from bson import ObjectId
from typing import List, Optional, Any
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate

class CRUDConversation:
    def create(self, db: Database, *, obj_in: ConversationCreate) -> Conversation:
        conversation_data = {
            "user_id": ObjectId(obj_in.user_id) if obj_in.user_id else None,
            "title": obj_in.title,
            "context": obj_in.context,
            "bot_response_count": obj_in.bot_response_count,
            "booking_status": obj_in.booking_status
        }
        
        collection = db.conversations
        result = collection.insert_one(conversation_data)
        
        # Get the created conversation
        created_conv = collection.find_one({"_id": result.inserted_id})
        # Convert ObjectId to string for the id field
        created_conv["id"] = str(created_conv["_id"])
        if created_conv.get("user_id"):
            created_conv["user_id"] = str(created_conv["user_id"])
        return Conversation(**created_conv)

    def get(self, db: Database, id: Any) -> Optional[Conversation]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.conversations
        result = collection.find_one({"_id": id})
        if result:
            # Convert ObjectId to string for the id field
            result["id"] = str(result["_id"])
            if result.get("user_id"):
                result["user_id"] = str(result["user_id"])
            return Conversation(**result)
        return None

    def get_by_user(self, db: Database, user_id: Any, skip: int = 0, limit: int = 100) -> List[Conversation]:
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return []
        collection = db.conversations
        cursor = collection.find({"user_id": user_id}).skip(skip).limit(limit)
        conversations = []
        for doc in cursor:
            # Convert ObjectId to string for the id field
            doc["id"] = str(doc["_id"])
            if doc.get("user_id"):
                doc["user_id"] = str(doc["user_id"])
            conversations.append(Conversation(**doc))
        return conversations

    def get_list_by_user(self, db: Database, user_id: Any, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get conversation list with message count and last message"""
        if isinstance(user_id, str):
            try:
                user_id = ObjectId(user_id)
            except:
                return []
        
        # Get conversations for user
        conversations = list(db.conversations.find({"user_id": user_id}).sort("updated_at", -1).skip(skip).limit(limit))
        
        result = []
        for conv in conversations:
            # Get message count for this conversation
            message_count = db.messages.count_documents({"conversation_id": conv["_id"]})
            
            # Get last message for this conversation
            last_message = db.messages.find_one(
                {"conversation_id": conv["_id"]}, 
                sort=[("created_at", -1)]
            )
            
            result.append({
                'id': str(conv["_id"]),
                'title': conv.get("title"),
                'context': conv.get("context"),
                'bot_response_count': conv.get("bot_response_count", 0),
                'booking_status': conv.get("booking_status"),
                'created_at': conv.get("created_at"),
                'updated_at': conv.get("updated_at"),
                'message_count': message_count,
                'last_message': last_message.get("content") if last_message else None
            })
        
        return result

    def update(self, db: Database, *, db_obj: Conversation, obj_in: ConversationUpdate) -> Conversation:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Convert string id back to ObjectId for MongoDB query
        conv_id = ObjectId(db_obj.id) if isinstance(db_obj.id, str) else db_obj.id
        
        collection = db.conversations
        collection.update_one(
            {"_id": conv_id},
            {"$set": update_data}
        )
        
        # Get the updated conversation
        updated_conv = collection.find_one({"_id": conv_id})
        updated_conv["id"] = str(updated_conv["_id"])
        if updated_conv.get("user_id"):
            updated_conv["user_id"] = str(updated_conv["user_id"])
        return Conversation(**updated_conv)

    def delete(self, db: Database, *, id: Any) -> Optional[Conversation]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = db.conversations
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            if doc.get("user_id"):
                doc["user_id"] = str(doc["user_id"])
            return Conversation(**doc)
        return None

class CRUDMessage:
    def create(self, db: Database, *, obj_in: MessageCreate, conversation_id: Any) -> Message:
        if isinstance(conversation_id, str):
            try:
                conversation_id = ObjectId(conversation_id)
            except:
                raise ValueError("Invalid conversation_id")
            
        message_data = {
            "conversation_id": conversation_id,
            "content": obj_in.content,
            "sender": obj_in.sender,
            "is_appropriate": obj_in.is_appropriate
        }
        
        collection = db.messages
        result = collection.insert_one(message_data)
        
        # Get the created message
        created_msg = collection.find_one({"_id": result.inserted_id})
        created_msg["id"] = str(created_msg["_id"])
        created_msg["conversation_id"] = str(created_msg["conversation_id"])
        return Message(**created_msg)

    def get_by_conversation(self, db: Database, conversation_id: Any, skip: int = 0, limit: int = 100) -> List[Message]:
        if isinstance(conversation_id, str):
            try:
                conversation_id = ObjectId(conversation_id)
            except:
                return []
            
        collection = db.messages
        cursor = collection.find({"conversation_id": conversation_id}).sort("created_at", 1).skip(skip).limit(limit)
        messages = []
        for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc["conversation_id"] = str(doc["conversation_id"])
            messages.append(Message(**doc))
        return messages

    def get(self, db: Database, id: Any) -> Optional[Message]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        collection = db.messages
        result = collection.find_one({"_id": id})
        if result:
            result["id"] = str(result["_id"])
            result["conversation_id"] = str(result["conversation_id"])
            return Message(**result)
        return None

    def delete(self, db: Database, *, id: Any) -> Optional[Message]:
        if isinstance(id, str):
            try:
                id = ObjectId(id)
            except:
                return None
        
        collection = db.messages
        doc = collection.find_one({"_id": id})
        if doc:
            collection.delete_one({"_id": id})
            doc["id"] = str(doc["_id"])
            doc["conversation_id"] = str(doc["conversation_id"])
            return Message(**doc)
        return None

conversation = CRUDConversation()
message = CRUDMessage() 