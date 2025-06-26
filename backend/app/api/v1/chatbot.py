from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.gemini import chat_with_gemini, format_conversation_history
from app.crud.crud_conversation import conversation, message
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.api.deps import get_current_user_optional, get_db
from app.models.user import User

router = APIRouter()

class Message(BaseModel):
    content: str
    sender: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    context: Optional[str] = 'consultant'

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    is_appropriate: bool = True

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        # Get or create conversation
        if request.conversation_id:
            # Get existing conversation
            conv = conversation.get(db, id=request.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
            
            # Check if user owns this conversation (if user is logged in)
            if current_user and conv.user_id and conv.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            # Create new conversation
            conv_data = ConversationCreate(
                user_id=current_user.id if current_user else None,
                context=request.context
            )
            conv = conversation.create(db, obj_in=conv_data)

        # Save user message
        user_message = MessageCreate(
            content=request.message,
            sender="user",
            is_appropriate=True
        )
        message.create(db, obj_in=user_message, conversation_id=conv.id)

        # Get conversation history for AI
        db_messages = message.get_by_conversation(db, conversation_id=conv.id)
        conversation_history = [
            {"content": msg.content, "sender": msg.sender}
            for msg in db_messages[:-1]  # Exclude the current user message
        ]

        # Get response from Gemini
        formatted_history = format_conversation_history(conversation_history)
        ai_response = chat_with_gemini(request.message, formatted_history, request.context)

        # Save AI response
        bot_message = MessageCreate(
            content=ai_response,
            sender="bot",
            is_appropriate=True
        )
        message.create(db, obj_in=bot_message, conversation_id=conv.id)

        # Update conversation title if it's the first message
        if not conv.title and len(db_messages) <= 2:  # User message + AI response
            # Generate title from first user message (truncate if too long)
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation.update(db, db_obj=conv, obj_in={"title": title})

        return ChatResponse(
            response=ai_response,
            conversation_id=conv.id,
            is_appropriate=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conversations = conversation.get_list_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return conversations

@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = message.get_by_conversation(db, conversation_id=conversation_id)
    
    return {
        "id": conv.id,
        "title": conv.title,
        "context": conv.context,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
        "messages": [
            {
                "id": msg.id,
                "content": msg.content,
                "sender": msg.sender,
                "is_appropriate": msg.is_appropriate,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    conversation.delete(db, id=conversation_id)
    return {"message": "Conversation deleted successfully"} 