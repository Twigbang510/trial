from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional, Union
from pymongo.database import Database
import re
from datetime import datetime
from app.core.gemini import chat_with_gemini, format_conversation_history
from app.core.booking_response_generator import booking_response_generator
from app.core import prompts
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
import httpx

logging.basicConfig(level=logging.DEBUG)
AI_MODULE_URL = "http://localhost:50/trial-ai/v1/kb_response"

logger = logging.getLogger(__name__)

router = APIRouter()

class Message(BaseModel):
    content: str
    sender: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[str] = 'consultant'

class BookingConfirmRequest(BaseModel):
    conversation_id: Union[str, int]
    availability_id: Union[str, int]
    lecturer_name: str
    date: str
    time: str
    subject: str
    location: str
    duration_minutes: int

@router.post("/confirm-booking", response_model=EnhancedChatResponse)
async def confirm_booking(
    request: BookingConfirmRequest,
    db: Database = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Direct booking confirmation endpoint - bypasses AI processing
    """
    try:
        # Convert IDs to strings for consistency
        conversation_id = str(request.conversation_id)
        availability_id = str(request.availability_id)
        
        # Get and validate conversation
        conv = ConversationService.get_or_create_conversation(db, conversation_id, current_user)
        ConversationService.validate_conversation_access(conv, current_user)
        
        # Check if conversation is already completed
        if ConversationService.check_conversation_completed(conv):
            return EnhancedChatResponse(
                response="This conversation has already been completed. The booking has already been confirmed.\n\nIf you need to make a new appointment, please start a new conversation.",
                conversation_id=conversation_id,
                is_appropriate=True,
                moderation_action="CLEAN",
                booking_options=[],
                needs_availability_check=False,
                suggested_next_action="complete"
            )
        
        ConversationService.save_user_message(db, "Yes", conversation_id)
        
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
            availability_id=availability_id,
            user=current_user,
            booking_date=request.date,
            booking_time=request.time,
            subject=request.subject
        )
        
        if booking_success:
            # Complete conversation and send email
            BookingService.complete_conversation(db, conversation_id)
            email_sent = BookingService.send_booking_confirmation_email(current_user, booking_details)
            success_message = BookingService.generate_success_message(booking_details, email_sent)
        else:
            success_message = BookingService.generate_failure_message()
            email_sent = False
        
        # Save bot response
        ConversationService.save_bot_message(db, success_message, conversation_id)
        
        # Create a simple response object to avoid ObjectId serialization issues
        response_data = {
            "response": success_message,
            "conversation_id": conversation_id,
            "is_appropriate": True,
            "moderation_action": "CLEAN",
            "booking_options": [],
            "needs_availability_check": False,
            "suggested_next_action": "complete",
            "email_sent": email_sent if booking_success else False,
            "booking_status": "complete" if booking_success else "ongoing"
        }
        
        # Debug logging
        print("Debug - Response data:", response_data)
        
        return EnhancedChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming booking: {e}")
        raise HTTPException(status_code=500, detail=f"Error confirming booking: {str(e)}")

@router.post("/cancel-booking", response_model=EnhancedChatResponse)
async def cancel_booking(
    request: ChatRequest,
    db: Database = Depends(get_db),
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
            conversation_id=str(request.conversation_id),
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
    db: Database = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    try:
        logger.debug(f"Received chat request: {request}")
        # 1. Check user status
        UserService.check_user_status(current_user)

        # 2. Moderation content (check if the message is appropriate)
        moderation_data = await ModerationService.moderate_user_content(request.message, current_user, db)
        if moderation_data["should_block"]:
            return EnhancedChatResponse(
                response="Your message has been blocked due to policy violations. Please ensure your messages are appropriate and constructive.",
                conversation_id=str(request.conversation_id or 0),
                is_appropriate=False,
                moderation_action="BLOCKED",
                warning_message=moderation_data["warning_message"]
            )
        if moderation_data["should_warn"]:
            current_user = moderation_data["updated_user"]

        # 3. Get or create conversation, check access
        conv = ConversationService.get_or_create_conversation(
            db, request.conversation_id, current_user, request.context or "consultant"
        )
        ConversationService.validate_conversation_access(conv, current_user)

        # 4. Check if conversation is completed
        if ConversationService.check_conversation_completed(conv):
            return EnhancedChatResponse(
                response="✅ This conversation has been completed. Your booking has been confirmed.\n\nIf you need to make a new appointment, please start a new conversation by refreshing the page.",
                conversation_id=str(getattr(conv, 'id')),
                is_appropriate=True,
                moderation_action="CLEAN",
                booking_options=[],
                needs_availability_check=False,
                suggested_next_action="complete"
            )

        # 5. Save user message, get history (only once)
        user_msg_obj = ConversationService.save_user_message(db, request.message, getattr(conv, 'id'))
        historical_messages = ConversationService.get_conversation_history(db, getattr(conv, 'id'))
        formatted_history = ConversationService.format_conversation_for_processing(historical_messages)

        # Build chat_history as a list of {role, content} (role: "TrialBot" if msg.sender == "bot", "contact" otherwise)
        chat_history = []
        for msg in historical_messages:
            role = "TrialBot" if msg.sender == "bot" else "contact"
            chat_history.append({"role": role, "content": msg.content})
        # Add the current user message to the chat history
        chat_history.append({"role": "contact", "content": request.message})

        ai_payload = {
            "question": request.message,
            "channel": "SMS",
            "chat_history": chat_history,
            "contact_id": str(getattr(current_user, 'id', '123'))
        }
        logging.info(f"[AI MODULE] Payload sent: {ai_payload}")
        async with httpx.AsyncClient(timeout=60) as client:
            ai_response = await client.post(AI_MODULE_URL, json=ai_payload)
        logging.info(f"[AI MODULE] Status: {ai_response.status_code}") 
        logging.info(f"[AI MODULE] Response received: {ai_response.text}")
        ai_response.raise_for_status()
        ai_data = ai_response.json()
        logger.debug(f"Received AI module response: {ai_data}")
        bot_reply = (
            ai_data.get("output")
            or ai_data.get("response")
            or (ai_data.get("final_response", {}).get("response") if isinstance(ai_data.get("final_response"), dict) else None)
            or ""
        )
        if not bot_reply or str(bot_reply).strip().lower() == "none":
            bot_reply = ""
        # Check if AI response indicates a booking should be created
        is_ai_booking = ai_data.get("isSchedule", False) and ai_data.get("datetime")
        ai_booking_result = None
        
        if is_ai_booking:
            logger.info(f"AI booking detected: {ai_data}")
            # Process AI booking response
            ai_booking_result = BookingService.process_ai_booking_response(
                db=db,
                ai_response=ai_data,
                conversation_id=str(getattr(conv, 'id')),
                user=current_user
            )
            
            # Use the processed message from booking service
            if ai_booking_result["success"]:
                bot_reply = ai_booking_result["message"]
            else:
                bot_reply = ai_booking_result["message"]
        
        ConversationService.save_bot_message(db, bot_reply, getattr(conv, 'id'))
        ConversationService.increment_bot_response_count(db, conv)
        ConversationService.update_conversation_title(db, conv, request.message)
        
        # Prepare response with AI booking data
        response_data = {
            "response": bot_reply,
            "conversation_id": str(getattr(conv, 'id')),
            "is_appropriate": True,
            "moderation_action": moderation_data["violation_type"],
            "warning_message": moderation_data["warning_message"],
            "booking_options": ai_data.get("booking_options", []),
            "needs_availability_check": ai_data.get("needs_availability_check", False),
            "suggested_next_action": ai_data.get("suggested_next_action", "provide_info"),
            "booking_analysis": ai_data.get("booking_analysis", None),
            "booking_status": ai_booking_result["booking_status"] if ai_booking_result else getattr(conv, 'booking_status', 'ongoing'),
            # AI Booking Response fields
            "ai_is_schedule": ai_data.get("isSchedule", False),
            "ai_booking_datetime": ai_data.get("datetime"),
            "ai_booking_timezone": ai_data.get("timezone"),
            "ai_booking_details": ai_booking_result["booking_details"] if ai_booking_result and ai_booking_result["success"] else None,
            "email_sent": ai_booking_result["email_sent"] if ai_booking_result else None
        }
        
        return EnhancedChatResponse(**response_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.post("/ai/kb_response")
async def proxy_kb_response(request: Request):
    try:
        input_data = await request.json()
        logger.info(f"Proxying request to AI module: {input_data}")
        async with httpx.AsyncClient(timeout=60) as client:
            ai_response = await client.post(AI_MODULE_URL, json=input_data)
        ai_response.raise_for_status()
        logger.info(f"Received response from AI module: {ai_response.text}")
        return ai_response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"AI module returned error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=502, detail=f"AI module error: {e.response.text}")
    except Exception as e:
        logger.error(f"Error proxying to AI module: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/conversations", response_model=List[dict])
async def get_conversations(
    skip: int = 0,
    limit: int = 100,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    validated_user = UserService.validate_user_access(current_user)
    conversations = conversation.get_list_by_user(db, user_id=str(getattr(validated_user, 'id')), skip=skip, limit=limit)
    return conversations

@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: str,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    validated_user = UserService.validate_user_access(current_user)
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    UserService.validate_user_access(validated_user, getattr(conv, 'user_id'))
    
    messages = message.get_by_conversation(db, conversation_id=conversation_id)
    
    conv_dict = conv.to_dict()
    
    return {
        "id": conv_dict["id"],
        "title": conv_dict.get("title"),
        "context": conv_dict.get("context"),
        "booking_status": conv_dict.get("booking_status", 'ongoing'),
        "created_at": conv_dict.get("created_at"),
        "updated_at": conv_dict.get("updated_at"),
        "messages": [
            {
                "id": str(msg.id),
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
    conversation_id: str,
    db: Database = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    validated_user = UserService.validate_user_access(current_user)
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    UserService.validate_user_access(validated_user, getattr(conv, 'user_id'))
    
    conversation.delete(db, id=conversation_id)
    return {"message": "Conversation deleted successfully"} 