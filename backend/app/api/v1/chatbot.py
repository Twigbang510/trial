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

# Keep old ChatResponse for backward compatibility
class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    is_appropriate: bool = True
    moderation_action: Optional[str] = None
    warning_message: Optional[str] = None

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
        
        # =================== ENHANCED BOOKING PROCESSING ===================
        # Process booking request with combined analysis + response + availability matching
        try:
            import time
            start_time = time.time()
            
            # Check if this is a booking confirmation (Yes response)
            is_booking_confirmation = await _check_booking_confirmation(
                request.message, conversation_history_str, db, conv, current_user
            )
            
            if is_booking_confirmation:
                # Booking confirmation was handled, return the response
                return is_booking_confirmation
            
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
            
            # Use the AI-generated response instead of calling Gemini again
            ai_response = booking_result.get("response_text", "")
            
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
            booking_analysis=analysis_data if 'analysis_data' in locals() else None
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

async def _check_booking_confirmation(
    user_message: str, 
    conversation_history: str, 
    db: Session, 
    conv, 
    current_user
) -> Optional[EnhancedChatResponse]:
    """
    Check if user message is a booking confirmation and handle it
    Returns EnhancedChatResponse if booking confirmation, None otherwise
    """
    try:
        # Check if message is a confirmation (Yes/Có/Đồng ý)
        confirmation_patterns = [
            r'\b(yes|có|đồng ý|ok|được|xác nhận|đặt lịch)\b',
            r'\b(y|yes)\b',
            r'^(yes|có|ok|được)$'
        ]
        
        is_confirmation = any(
            re.search(pattern, user_message.lower().strip(), re.IGNORECASE) 
            for pattern in confirmation_patterns
        )
        
        if not is_confirmation:
            return None
        
        # Extract booking details from conversation history
        booking_details = _extract_booking_details_from_history(conversation_history)
        
        if not booking_details:
            return None
        
        # Create the booking
        booking_slot = lecturer_availability.create_booking_slot(
            db=db,
            availability_id=booking_details['availability_id'],
            user_id=getattr(current_user, 'id') if current_user else None,
            booking_date=booking_details['date'],
            booking_time=booking_details['time'],
            subject=booking_details['subject'],
            notes=f"Confirmed via chat at {datetime.now().isoformat()}"
        )
        
        if booking_slot:
            # Update conversation status to complete
            conversation.update(
                db, 
                db_obj=conv, 
                obj_in=ConversationUpdate(booking_status="complete")
            )
            
            # Create success message
            success_message = f"✅ **Đặt lịch thành công!**\n\n"
            success_message += f"📅 **Thông tin lịch hẹn:**\n"
            success_message += f"• **Giảng viên:** {booking_details['lecturer_name']}\n"
            success_message += f"• **Thời gian:** {booking_details['time']} - {booking_details['date']}\n"
            success_message += f"• **Môn học:** {booking_details['subject']}\n"
            success_message += f"• **Địa điểm:** {booking_details['location']}\n"
            success_message += f"• **Thời lượng:** {booking_details['duration_minutes']} phút\n\n"
            success_message += f"📧 Bạn sẽ nhận được email xác nhận sớm nhất.\n"
            success_message += f"🔔 Lưu ý: Vui lòng có mặt đúng giờ và chuẩn bị đầy đủ tài liệu cần thiết.\n\n"
            success_message += f"Cảm ơn bạn đã sử dụng dịch vụ!"
            
        else:
            # Booking failed
            success_message = "❌ **Không thể đặt lịch**\n\n"
            success_message += "Rất tiếc, khung giờ này có thể đã được đặt bởi người khác. "
            success_message += "Vui lòng chọn khung giờ khác hoặc thử lại sau."
        
        # Save bot response
        bot_message = MessageCreate(
            content=success_message,
            sender="bot",
            is_appropriate=True
        )
        message.create(db, obj_in=bot_message, conversation_id=getattr(conv, 'id'))
        
        return EnhancedChatResponse(
            response=success_message,
            conversation_id=getattr(conv, 'id'),
            is_appropriate=True,
            moderation_action="CLEAN",
            booking_options=[],
            needs_availability_check=False,
            suggested_next_action="complete"
        )
        
    except Exception as e:
        logger.error(f"Error handling booking confirmation: {e}")
        return None

def _extract_booking_details_from_history(conversation_history: str) -> Optional[dict]:
    """
    Extract booking details from conversation history
    Look for confirmation messages that contain booking details
    """
    try:
        # Look for confirmation message pattern
        confirmation_pattern = r"Do you want to confirm your booking with (.+?) on (.+?) at (.+?) for (.+?)\?"
        match = re.search(confirmation_pattern, conversation_history, re.IGNORECASE)
        
        if match:
            lecturer_name = match.group(1).strip()
            date = match.group(2).strip()
            time = match.group(3).strip()
            subject = match.group(4).strip()
            
            # Extract additional details from available time slots in history
            # Look for availability_id in booking options
            availability_pattern = r'"availability_id":\s*(\d+)'
            avail_match = re.search(availability_pattern, conversation_history)
            availability_id = int(avail_match.group(1)) if avail_match else None
            
            # Extract location and duration
            location_pattern = r'"location":\s*"([^"]*)"'
            duration_pattern = r'"duration_minutes":\s*(\d+)'
            
            location_match = re.search(location_pattern, conversation_history)
            duration_match = re.search(duration_pattern, conversation_history)
            
            return {
                'lecturer_name': lecturer_name,
                'date': date,
                'time': time,
                'subject': subject,
                'location': location_match.group(1) if location_match else 'TBD',
                'duration_minutes': int(duration_match.group(1)) if duration_match else 30,
                'availability_id': availability_id
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error extracting booking details: {e}")
        return None 