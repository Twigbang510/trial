from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import re
from datetime import datetime
from app.core.gemini import chat_with_gemini, format_conversation_history
from app.core.booking_response_generator import booking_response_generator
from app.crud.crud_conversation import conversation, message
from app.crud import booking_analysis
from app.schemas.conversation import ConversationCreate, MessageCreate, EnhancedChatResponse, BookingOption, ConversationUpdate
from app.api.deps import get_current_user_optional, get_db
from app.models.user import User
from app.services.user_service import UserService
from app.services.booking_service import BookingService
from app.services.conversation_service import ConversationService
from app.services.moderation_service import ModerationService
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

class BookingConfirmRequest(BaseModel):
    conversation_id: int
    availability_id: int
    lecturer_name: str
    date: str
    time: str
    subject: str
    location: str
    duration_minutes: int

# Keep old ChatResponse for backward compatibility
class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    is_appropriate: bool = True
    moderation_action: Optional[str] = None
    warning_message: Optional[str] = None

@router.post("/confirm-booking", response_model=EnhancedChatResponse)
async def confirm_booking(
    request: BookingConfirmRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Direct booking confirmation endpoint - bypasses AI processing
    """
    try:
        # Get and validate conversation
        conv = ConversationService.get_or_create_conversation(db, request.conversation_id, current_user)
        ConversationService.validate_conversation_access(conv, current_user)
        
        # Check if conversation is already completed
        if ConversationService.check_conversation_completed(conv):
            return EnhancedChatResponse(
                response="❌ **This conversation has already been completed.** The booking has already been confirmed.\n\nIf you need to make a new appointment, please start a new conversation.",
                conversation_id=request.conversation_id,
                is_appropriate=True,
                moderation_action="CLEAN",
                booking_options=[],
                needs_availability_check=False,
                suggested_next_action="complete"
            )
        
        ConversationService.save_user_message(db, "Yes", request.conversation_id)
        
        # Prepare booking details
        booking_details = {
            'lecturer_name': request.lecturer_name,
            'date': request.date,
            'time': request.time,
            'subject': request.subject,
            'location': request.location,
            'duration_minutes': request.duration_minutes
        }
        
        # Attempt to create booking
        booking_success = BookingService.create_booking_slot(
            db=db,
            availability_id=request.availability_id,
            user=current_user,
            booking_date=request.date,
            booking_time=request.time,
            subject=request.subject
        )
        
        if booking_success:
            # Complete conversation and send email
            BookingService.complete_conversation(db, request.conversation_id)
            email_sent = BookingService.send_booking_confirmation_email(current_user, booking_details)
            success_message = BookingService.generate_success_message(booking_details, email_sent)
        else:
            success_message = BookingService.generate_failure_message()
            email_sent = False
        
        # Save bot response
        ConversationService.save_bot_message(db, success_message, request.conversation_id)
        
        return EnhancedChatResponse(
            response=success_message,
            conversation_id=request.conversation_id,
            is_appropriate=True,
            moderation_action="CLEAN",
            booking_options=[],
            needs_availability_check=False,
            suggested_next_action="complete",
            email_sent=email_sent if booking_success else False,
            booking_status="complete" if booking_success else "ongoing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error confirming booking: {str(e)}")

@router.post("/cancel-booking", response_model=EnhancedChatResponse)
async def cancel_booking(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Handle booking cancellation - allows user to continue chatting
    """
    try:
        # Get and validate conversation
        conv = ConversationService.get_or_create_conversation(db, request.conversation_id, current_user)
        
        # Save user's "No" message and bot's continue message
        ConversationService.save_user_message(db, "No", request.conversation_id)
        continue_message = "No problem! I can help you find another time or answer any more questions about booking. Do you need any more help?"
        ConversationService.save_bot_message(db, continue_message, request.conversation_id)
        
        return EnhancedChatResponse(
            response=continue_message,
            conversation_id=request.conversation_id,
            is_appropriate=True,
            moderation_action="CLEAN",
            booking_options=[],
            needs_availability_check=False,
            suggested_next_action="provide_info"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error canceling booking: {str(e)}")

@router.post("/chat", response_model=EnhancedChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        # Check user status
        UserService.check_user_status(current_user)
        
        # Moderate content and handle violations
        moderation_data = await ModerationService.moderate_user_content(request.message, current_user, db)
        
        if moderation_data["should_block"]:
            return EnhancedChatResponse(
                response="Your message has been blocked due to policy violations. Please ensure your messages are appropriate and constructive.",
                conversation_id=request.conversation_id or 0,
                is_appropriate=False,
                moderation_action="BLOCKED",
                warning_message=moderation_data["warning_message"]
            )
        
        # Update current_user if violations were handled
        if moderation_data["should_warn"]:
            current_user = moderation_data["updated_user"]
        
        # Get or create conversation
        conv = ConversationService.get_or_create_conversation(
            db, request.conversation_id, current_user, request.context or "consultant"
        )
        
        # Validate access and check completion status
        ConversationService.validate_conversation_access(conv, current_user)
        
        if ConversationService.check_conversation_completed(conv):
            return EnhancedChatResponse(
                response="✅ **This conversation has been completed.** Your booking has been confirmed.\n\nIf you need to make a new appointment, please start a new conversation by refreshing the page.",
                conversation_id=getattr(conv, 'id'),
                is_appropriate=True,
                moderation_action="CLEAN",
                booking_options=[],
                needs_availability_check=False,
                suggested_next_action="complete"
            )

        # Save user message and get conversation history
        user_msg_obj = ConversationService.save_user_message(db, request.message, getattr(conv, 'id'))
        historical_messages = ConversationService.get_conversation_history(db, getattr(conv, 'id'))
        
        # Check conversation limits
        future_bot_count = getattr(conv, 'bot_response_count', 0) + 1
        if ConversationService.should_stop_conversation(conv, future_bot_count):
            stop_message = ConversationService.abandon_conversation(db, conv)
            ConversationService.save_bot_message(db, stop_message, getattr(conv, 'id'))
            
            return EnhancedChatResponse(
                response=stop_message,
                conversation_id=getattr(conv, 'id'),
                is_appropriate=True,
                moderation_action="CLEAN"
            )
        
        # Prepare conversation for processing
        conversation_history_str = ConversationService.format_conversation_for_processing(historical_messages)
        ConversationService.update_conversation_status(db, conv, request.message, conversation_history_str)
        
        # BOOKING PROCESSING
        try:
            import time
            start_time = time.time()
            
            booking_result = await booking_response_generator.process_booking_request(
                user_message=request.message,
                conversation_history=conversation_history_str,
                db_session=db
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            analysis_data = {
                "intent": booking_result.get("intent"),
                "safety_score": booking_result.get("safety_score"),
                "is_rejection": booking_result.get("is_rejection"),
                "is_confirmation": booking_result.get("is_confirmation"),
                "input_slots": booking_result.get("input_slots"),
                "time_range": booking_result.get("time_range"),
                "date": booking_result.get("date"),
                "reasoning": booking_result.get("reasoning")
            }
            
            booking_analysis.create_analysis(
                db=db,
                conversation_id=int(getattr(conv, 'id')),
                message_id=int(getattr(user_msg_obj, 'id')),
                analysis_result=analysis_data,
                processing_time_ms=processing_time_ms
            )
            
            if booking_result.get("intent") == "A" and booking_result.get("is_confirmation"):
                setattr(conv, 'booking_status', "completed")
                conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(booking_status="completed"))
            
            intent = booking_result.get("intent", "O")
            input_slots = booking_result.get("input_slots", [])
            time_range = booking_result.get("time_range", [])
            booking_options = booking_result.get("booking_options", [])
            ai_response = booking_result.get("response_text", "")
            
            should_use_general_chat = (
                intent == "O" or
                (intent == "C" and not input_slots and not time_range and not booking_options)
            )
            
            if should_use_general_chat:
                conversation_history = [
                    {"content": msg.content, "sender": msg.sender}
                    for msg in historical_messages
                ]
                
                formatted_history = format_conversation_history(conversation_history)
                ai_response = chat_with_gemini(request.message, formatted_history, request.context or "consultant")
                
                booking_result.update({
                    "response_text": ai_response,
                    "booking_options": [],
                    "needs_availability_check": False,
                    "suggested_next_action": "provide_info"
                })

            else:
                # Only apply fallback logic if booking_response_generator clearly failed
                if intent == "O" and not input_slots and not time_range and not booking_options:
                    # This is truly general chat, not booking-related
                    pass
                elif intent == "C" and not input_slots and not time_range and not booking_options:
                    # Booking inquiry but no specific information extracted
                    ai_response = "Tôi có thể giúp bạn tìm thời gian phù hợp! Bạn muốn đặt lịch vào thời gian nào?"
                    booking_result["response_text"] = ai_response
            
        except Exception as e:
            logger.error(f"Enhanced booking processing failed: {e}")
            conversation_history = [
                {"content": msg.content, "sender": msg.sender}
                for msg in historical_messages
            ]
            
            formatted_history = format_conversation_history(conversation_history)
            ai_response = chat_with_gemini(request.message, formatted_history, request.context or "consultant")
            booking_result = {
                "response_text": ai_response,
                "booking_options": [],
                "needs_availability_check": False,
                "suggested_next_action": "provide_info"
            }

        # Save bot response and update conversation
        ConversationService.save_bot_message(db, ai_response, getattr(conv, 'id'))
        ConversationService.increment_bot_response_count(db, conv)
        ConversationService.update_conversation_title(db, conv, request.message)

        booking_options = [
            BookingOption(**option) for option in booking_result.get("booking_options", [])
        ]

        return EnhancedChatResponse(
            response=ai_response,
            conversation_id=getattr(conv, 'id'),
            is_appropriate=True,
            moderation_action=moderation_data["violation_type"],
            warning_message=moderation_data["warning_message"],
            booking_options=booking_options,
            needs_availability_check=booking_result.get("needs_availability_check", False),
            suggested_next_action=booking_result.get("suggested_next_action", "provide_info"),
            booking_analysis=analysis_data if 'analysis_data' in locals() else None,
            booking_status=getattr(conv, 'booking_status', 'ongoing')
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
    validated_user = UserService.validate_user_access(current_user)
    conversations = conversation.get_list_by_user(db, user_id=int(getattr(validated_user, 'id')), skip=skip, limit=limit)
    return conversations

@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    validated_user = UserService.validate_user_access(current_user)
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    UserService.validate_user_access(validated_user, getattr(conv, 'user_id'))
    
    messages = message.get_by_conversation(db, conversation_id=conversation_id)
    
    return {
        "id": getattr(conv, 'id'),
        "title": getattr(conv, 'title'),
        "context": getattr(conv, 'context'),
        "booking_status": getattr(conv, 'booking_status', 'ongoing'),
        "created_at": getattr(conv, 'created_at'),
        "updated_at": getattr(conv, 'updated_at'),
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
    validated_user = UserService.validate_user_access(current_user)
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    UserService.validate_user_access(validated_user, getattr(conv, 'user_id'))
    
    conversation.delete(db, id=conversation_id)
    return {"message": "Conversation deleted successfully"} 