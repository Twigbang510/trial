from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
import re
from datetime import datetime
from app.core.gemini import chat_with_gemini, format_conversation_history
from app.core.moderation import moderate_content
from app.core.chat_history import ChatHistoryManager
from app.core.booking_response_generator import booking_response_generator
from app.crud.crud_conversation import conversation, message
from app.crud.crud_user import user_crud
from app.crud import booking_analysis, lecturer_availability
from app.schemas.conversation import ConversationCreate, MessageCreate, EnhancedChatResponse, BookingOption, ConversationUpdate
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
        # Validate conversation exists and user has access
        conv = conversation.get(db, id=request.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Check if conversation is already completed
        if getattr(conv, 'booking_status') == 'complete':
            return EnhancedChatResponse(
                response="❌ **This conversation has already been completed.** The booking has already been confirmed.\n\nIf you need to make a new appointment, please start a new conversation.",
                conversation_id=request.conversation_id,
                is_appropriate=True,
                moderation_action="CLEAN",
                booking_options=[],
                needs_availability_check=False,
                suggested_next_action="complete"
            )
        
        if current_user and getattr(conv, 'user_id') and int(getattr(conv, 'user_id')) != int(getattr(current_user, 'id')):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Add user's "Yes" message
        user_message = MessageCreate(
            content="Yes",
            sender="user",
            is_appropriate=True
        )
        user_msg_obj = message.create(db, obj_in=user_message, conversation_id=request.conversation_id)
        
        # Create the booking directly
        booking_slot = lecturer_availability.create_booking_slot(
            db=db,
            availability_id=request.availability_id,
            user_id=getattr(current_user, 'id') if current_user else None,
            booking_date=request.date,
            booking_time=request.time,
            subject=request.subject,
            notes=f"Confirmed via chat at {datetime.now().isoformat()}"
        )
        
        if booking_slot:
            # Update conversation status to complete
            conversation.update(
                db, 
                db_obj=conv, 
                obj_in=ConversationUpdate(booking_status="complete")
            )
            
            # Send email confirmation if user has email
            email_sent = False
            if current_user and hasattr(current_user, 'email') and current_user.email:
                from app.core.email import send_booking_confirmation_email
                booking_details = {
                    'lecturer_name': request.lecturer_name,
                    'date': request.date,
                    'time': request.time,
                    'subject': request.subject,
                    'location': request.location,
                    'duration_minutes': request.duration_minutes
                }
                email_sent = send_booking_confirmation_email(current_user.email, booking_details)
            
            # Create enhanced success message
            success_message = "🎉 **Booking Confirmed Successfully!**\n\n"
            success_message += "📅 **Your Appointment Details:**\n"
            success_message += f"👨‍🏫 **Lecturer:** {request.lecturer_name}\n"
            success_message += f"📅 **Date:** {request.date}\n"
            success_message += f"⏰ **Time:** {request.time}\n"
            success_message += f"📚 **Subject:** {request.subject}\n"
            success_message += f"📍 **Location:** {request.location}\n"
            success_message += f"⏱️ **Duration:** {request.duration_minutes} minutes\n\n"
            
            if email_sent:
                success_message += "📧 **Email Confirmation Sent!** Check your inbox for detailed booking information.\n\n"
            else:
                success_message += "📧 Email confirmation will be sent shortly.\n\n"
                
            
        else:
            # Booking failed
            success_message = "❌ **Unable to Complete Booking**\n\n"
            success_message += "This time slot may have been taken by another student. "
            success_message += "Please try selecting a different time slot.\n\n"
            success_message += "💡 **Tip:** Popular time slots fill up quickly. Consider booking alternative times for better availability."
        
        # Save bot response
        bot_message = MessageCreate(
            content=success_message,
            sender="bot",
            is_appropriate=True
        )
        message.create(db, obj_in=bot_message, conversation_id=request.conversation_id)
        
        return EnhancedChatResponse(
            response=success_message,
            conversation_id=request.conversation_id,
            is_appropriate=True,
            moderation_action="CLEAN",
            booking_options=[],
            needs_availability_check=False,
            suggested_next_action="complete",
            email_sent=email_sent if booking_slot else False,
            booking_status="complete" if booking_slot else "ongoing"
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
        # Validate conversation
        conv = conversation.get(db, id=request.conversation_id)
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Add user's "No" message
        user_message = MessageCreate(
            content="No",
            sender="user",
            is_appropriate=True
        )
        message.create(db, obj_in=user_message, conversation_id=request.conversation_id)
        
        # Add bot's continue message
        continue_message = "No problem! I can help you find another time or answer any more questions about booking. Do you need any more help?"
        
        bot_message = MessageCreate(
            content=continue_message,
            sender="bot",
            is_appropriate=True
        )
        message.create(db, obj_in=bot_message, conversation_id=request.conversation_id)
        
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
        # Check if user is active
        if current_user and not bool(current_user.is_active):
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
                if not bool(updated_user.is_active):
                    raise HTTPException(
                        status_code=403,
                        detail="Your account has been suspended due to repeated policy violations. Please contact support."
                    )
            
            # Return blocked response
            return EnhancedChatResponse(
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
                if not bool(updated_user.is_active):
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
            
            # Check if conversation is completed - block further messages
            if getattr(conv, 'booking_status') == 'complete':
                return EnhancedChatResponse(
                    response="✅ **This conversation has been completed.** Your booking has been confirmed.\n\nIf you need to make a new appointment, please start a new conversation by refreshing the page.",
                    conversation_id=request.conversation_id,
                    is_appropriate=True,
                    moderation_action="CLEAN",
                    booking_options=[],
                    needs_availability_check=False,
                    suggested_next_action="complete"
                )
            
            # Check if user owns this conversation (if user is logged in)
            if current_user and conv.user_id and int(getattr(conv, 'user_id')) != int(getattr(current_user, 'id')):
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            # Create new conversation
            conv_data = ConversationCreate(
                user_id=getattr(current_user, 'id') if current_user else None,
                context=request.context or "consultant"
            )
            conv = conversation.create(db, obj_in=conv_data)

        # Save user message
        user_message = MessageCreate(
            content=request.message,
            sender="user",
            is_appropriate=True
        )
        user_msg_obj = message.create(db, obj_in=user_message, conversation_id=getattr(conv, 'id'))

        # Get conversation history for AI and chat analysis
        db_messages = message.get_by_conversation(db, conversation_id=getattr(conv, 'id'))
        
        # Analyze conversation history (excluding current user message)
        historical_messages = db_messages[:-1] if db_messages else []
        history_analysis = ChatHistoryManager.analyze_conversation_history(historical_messages)
        
        future_bot_count = getattr(conv, 'bot_response_count', 0) + 1
        if ChatHistoryManager.should_stop_conversation(conv, future_bot_count):
            # Update conversation status to abandoned if not already
            if getattr(conv, 'booking_status') != "abandoned":
                setattr(conv, 'booking_status', "abandoned")
                conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(booking_status="abandoned"))
            
            # Return stop message
            stop_message = ChatHistoryManager.get_stop_message()
            
            # Save the stop message as bot response
            bot_message = MessageCreate(
                content=stop_message,
                sender="bot",
                is_appropriate=True
            )
            message.create(db, obj_in=bot_message, conversation_id=getattr(conv, 'id'))
            
            return EnhancedChatResponse(
                response=stop_message,
                conversation_id=getattr(conv, 'id'),
                is_appropriate=True,
                moderation_action="CLEAN"
            )
        
        # Update conversation status based on user message
        conversation_history_str = ChatHistoryManager.convert_messages_to_history_string(historical_messages)
        ChatHistoryManager.update_conversation_status(db, conv, request.message, conversation_history_str)
        
        # =================== BOOKING PROCESSING ===================
        # Process booking request with combined analysis + response + availability matching
        try:
            import time
            start_time = time.time()
            
            # Run enhanced booking processing (ONE API CALL)
            booking_result = await booking_response_generator.process_booking_request(
                user_message=request.message,
                conversation_history=conversation_history_str,
                db_session=db
            )
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Save booking analysis to database
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
            
            print(f"Enhanced booking analysis completed for message {user_msg_obj.id}: {analysis_data}")
            
            # Check if user confirmed a booking (intent A and is_confirmation)
            if booking_result.get("intent") == "A" and booking_result.get("is_confirmation"):
                # Update conversation status to completed
                setattr(conv, 'booking_status', "completed")
                conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(booking_status="completed"))
                print(f"Conversation {getattr(conv, 'id')} marked as completed due to booking confirmation")
            
            # Extract booking analysis results
            intent = booking_result.get("intent", "O")
            input_slots = booking_result.get("input_slots", [])
            time_range = booking_result.get("time_range", [])
            booking_options = booking_result.get("booking_options", [])
            ai_response = booking_result.get("response_text", "")
            
            # Determine if we should fallback to general chat
            should_use_general_chat = (
                intent == "O" or  # Out of scope
                (intent == "C" and not input_slots and not time_range and not booking_options)  # General inquiry without specific time/options
            )
            
            if should_use_general_chat:
                # Fallback to general chat with Gemini for non-booking questions
                conversation_history = [
                    {"content": msg.content, "sender": msg.sender}
                    for msg in historical_messages
                ]
                
                formatted_history = format_conversation_history(conversation_history)
                ai_response = chat_with_gemini(request.message, formatted_history, request.context or "consultant")
                
                # Update booking_result for consistent response format
                booking_result.update({
                    "response_text": ai_response,
                    "booking_options": [],
                    "needs_availability_check": False,
                    "suggested_next_action": "provide_info"
                })
                
                print(f"Used general chat for intent {intent} - message: {request.message[:50]}...")
            else:
                # Handle booking-related responses
                if intent == "C" and not time_range and not booking_options:
                    # Keep AI response as is for general availability questions
                    pass  
                elif intent == "O" or (not time_range and not booking_options):
                    # Clean up booking-specific error messages for edge cases
                    if "❌" in ai_response and ("không có thời gian" in ai_response.lower() or "no matching" in ai_response.lower()):
                        ai_response = "I'm here to help you with appointment scheduling. Please let me know what specific time you'd prefer, or ask about lecturer availability, and I'll assist you in finding the best options."
                        booking_result["response_text"] = ai_response
            
        except Exception as e:
            logger.error(f"Enhanced booking processing failed: {e}")
            # Fallback to normal chat flow
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

        # Save AI response
        bot_message = MessageCreate(
            content=ai_response,
            sender="bot",
            is_appropriate=True
        )
        message.create(db, obj_in=bot_message, conversation_id=getattr(conv, 'id'))
        
        # Increment bot response count after generating response
        ChatHistoryManager.increment_bot_response_count(db, conv)

        # Update conversation title if it's the first message
        if not getattr(conv, 'title') and len(db_messages) <= 2:  # User message + AI response
            # Generate title from first user message (truncate if too long)
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation.update(db, db_obj=conv, obj_in=ConversationUpdate(title=title))

        # Prepare warning message if needed
        warning_message = None
        if should_warn(moderation_result):
            remaining_violations = 5 - (getattr(current_user, 'violation_count') if current_user else 0)
            if remaining_violations < 0:
                remaining_violations = 0
            warning_message = f"Your message contains potentially inappropriate content. You have {remaining_violations} warnings remaining before account suspension."

        # Convert booking options to Pydantic models
        booking_options = [
            BookingOption(**option) for option in booking_result.get("booking_options", [])
        ]

        return EnhancedChatResponse(
            response=ai_response,
            conversation_id=getattr(conv, 'id'),
            is_appropriate=True,
            moderation_action=moderation_result.get('violation_type', 'CLEAN'),
            warning_message=warning_message,
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
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not bool(current_user.is_active):
        raise HTTPException(status_code=403, detail="Account suspended")
    
    conversations = conversation.get_list_by_user(db, user_id=int(getattr(current_user, 'id')), skip=skip, limit=limit)
    return conversations

@router.get("/conversations/{conversation_id}", response_model=dict)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not bool(current_user.is_active):
        raise HTTPException(status_code=403, detail="Account suspended")
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if getattr(conv, 'user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
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
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if not bool(current_user.is_active):
        raise HTTPException(status_code=403, detail="Account suspended")
    
    conv = conversation.get(db, id=conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if getattr(conv, 'user_id') != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    conversation.delete(db, id=conversation_id)
    return {"message": "Conversation deleted successfully"} 