from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import ConversationCreate, ConversationUpdate, MessageCreate

class CRUDConversation:
    def create(self, db: Session, *, obj_in: ConversationCreate) -> Conversation:
        db_obj = Conversation(
            user_id=obj_in.user_id,
            title=obj_in.title,
            context=obj_in.context
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[Conversation]:
        return db.query(Conversation).filter(Conversation.id == id).first()

    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Conversation]:
        return db.query(Conversation).filter(Conversation.user_id == user_id).offset(skip).limit(limit).all()

    def get_list_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Get conversation list with message count and last message"""
        conversations = db.query(
            Conversation,
            func.count(Message.id).label('message_count'),
            func.max(Message.content).label('last_message')
        ).outerjoin(Message).filter(
            Conversation.user_id == user_id
        ).group_by(Conversation.id).order_by(
            Conversation.updated_at.desc()
        ).offset(skip).limit(limit).all()
        
        result = []
        for conv, msg_count, last_msg in conversations:
            result.append({
                'id': conv.id,
                'title': conv.title,
                'context': conv.context,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at,
                'message_count': msg_count,
                'last_message': last_msg
            })
        
        return result

    def update(self, db: Session, *, db_obj: Conversation, obj_in: ConversationUpdate) -> Conversation:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Conversation:
        obj = db.query(Conversation).get(id)
        db.delete(obj)
        db.commit()
        return obj

class CRUDMessage:
    def create(self, db: Session, *, obj_in: MessageCreate, conversation_id: int) -> Message:
        db_obj = Message(
            conversation_id=conversation_id,
            content=obj_in.content,
            sender=obj_in.sender,
            is_appropriate=obj_in.is_appropriate
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation(self, db: Session, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

    def get(self, db: Session, id: int) -> Optional[Message]:
        return db.query(Message).filter(Message.id == id).first()

    def delete(self, db: Session, *, id: int) -> Message:
        obj = db.query(Message).get(id)
        db.delete(obj)
        db.commit()
        return obj

conversation = CRUDConversation()
message = CRUDMessage() 