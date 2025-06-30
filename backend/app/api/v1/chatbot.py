from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.gemini import chat_with_gemini, format_conversation_history
from app.core.moderation import moderate_content
from app.core.chat_history import ChatHistoryManager
from app.crud.crud_conversation import conversation, message
from app.crud.crud_user import user_crud
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.api.deps import get_current_user_optional, get_db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

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
    moderation_action: Optional[str] = None  # "CLEAN", "WARNING", "BLOCKED"
    warning_message: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        # Check if user is active
        if current_user and not current_user.is_active:
            raise HTTPException(
                status_code=403, 
                detail="Your account has been suspended due to policy violations. Please contact support."
            )
        
        # Moderate the user's message
        moderation_result = await moderate_content(request.message)
        print("moderation_result", moderation_result)
        
        # Helper functions to check moderation result (dictionary format)
        def should_block(mod_result):
            """Check if content should be blocked"""
            return mod_result.get('violation_type') == 'BLOCK'
        
        def should_warn(mod_result):
            """Check if content should trigger warning"""
            return mod_result.get('violation_type') == 'WARNING'
        
        # Handle blocked content
        if should_block(moderation_result):
            if current_user:
                # Increment violation count and potentially deactivate user
                updated_user = user_crud.increment_violation(
                    db=db, 
                    user=current_user, 
                    violation_type="BLOCK"
                )
                logger.warning(f"User {current_user.id} content blocked. Violations: {updated_user.violation_count}")
                
                # If user is now deactivated, inform them
                if not updated_user.is_active:
                    raise HTTPException(
                        status_code=403,
                        detail="Your account has been suspended due to repeated policy violations. Please contact support."
                    )
            
            # Return blocked response
            return ChatResponse(
                response="Your message has been blocked due to policy violations. Please ensure your messages are appropriate and constructive.",
                conversation_id=request.conversation_id or 0,
                is_appropriate=False,
                moderation_action="BLOCKED",
                warning_message="Content blocked due to policy violations. Repeated violations may result in account suspension."
            )
        
        # Handle warning content
        if should_warn(moderation_result):
            if current_user:
                # Increment violation count
                updated_user = user_crud.increment_violation(
                    db=db, 
                    user=current_user, 
                    violation_type="WARNING"
                )
                logger.info(f"User {current_user.id} content warning. Violations: {updated_user.violation_count}")
                
                # Check if user is now suspended after this violation
                if not updated_user.is_active:
                    raise HTTPException(
                        status_code=403,
                        detail="Your account has been suspended due to repeated policy violations. Please contact support."
                    )
                
                # Update current_user reference for remaining calculations
                current_user = updated_user
        
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

        # Get conversation history for AI and chat analysis
        db_messages = message.get_by_conversation(db, conversation_id=conv.id)
        
        # Analyze conversation history (excluding current user message)
        historical_messages = db_messages[:-1] if db_messages else []
        history_analysis = ChatHistoryManager.analyze_conversation_history(historical_messages)
        
        future_bot_count = conv.bot_response_count + 1
        if ChatHistoryManager.should_stop_conversation(conv, future_bot_count):
            # Update conversation status to abandoned if not already
            if conv.booking_status != "abandoned":
                conv.booking_status = "abandoned"
                conversation.update(db, db_obj=conv, obj_in={"booking_status": "abandoned"})
            
            # Return stop message
            stop_message = ChatHistoryManager.get_stop_message()
            
            # Save the stop message as bot response
            bot_message = MessageCreate(
                content=stop_message,
                sender="bot",
                is_appropriate=True
            )
            message.create(db, obj_in=bot_message, conversation_id=conv.id)
            
            return ChatResponse(
                response=stop_message,
                conversation_id=conv.id,
                is_appropriate=True,
                moderation_action="CLEAN"
            )
        
        # Update conversation status based on user message
        conversation_history_str = ChatHistoryManager.convert_messages_to_history_string(historical_messages)
        ChatHistoryManager.update_conversation_status(db, conv, request.message, conversation_history_str)
        
        # Format conversation history for AI
        conversation_history = [
            {"content": msg.content, "sender": msg.sender}
            for msg in historical_messages
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
        
        # Increment bot response count after generating response
        ChatHistoryManager.increment_bot_response_count(db, conv)

        # Update conversation title if it's the first message
        if not conv.title and len(db_messages) <= 2:  # User message + AI response
            # Generate title from first user message (truncate if too long)
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation.update(db, db_obj=conv, obj_in={"title": title})

        # Prepare warning message if needed
        warning_message = None
        if should_warn(moderation_result):
            # Use updated violation count (current_user was updated above if there was a warning)
            remaining_violations = 5 - (current_user.violation_count if current_user else 0)
            if remaining_violations < 0:
                remaining_violations = 0  # Never show negative numbers
            warning_message = f"Your message contains potentially inappropriate content. You have {remaining_violations} warnings remaining before account suspension."

        return ChatResponse(
            response=ai_response,
            conversation_id=conv.id,
            is_appropriate=True,
            moderation_action=moderation_result.get('violation_type', 'CLEAN'),
            warning_message=warning_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
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
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")
    
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
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")
    
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
    
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    conversation.delete(db, id=conversation_id)
    return {"message": "Conversation deleted successfully"} 