from app.db.session import database
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.career_analysis import CareerAnalysis
from app.models.booking_analysis import BookingAnalysis
from app.models.lecturer_availability import LecturerAvailability, BookingSlot

def init_db():
    """Initialize MongoDB collections and indexes"""
    try:
        database.users.create_index("email", unique=True, name="email_unique")
    except Exception as e:
        print(f"Index creation warning (users.email): {e}")
    try:
        database.users.create_index("username", unique=True, name="username_unique")
    except Exception as e:
        print(f"Index creation warning (users.username): {e}")
    
    # Create indexes for conversations collection
    try:
        database.conversations.create_index("user_id", name="conv_user_id")
        database.conversations.create_index("created_at", name="conv_created_at")
    except Exception as e:
        print(f"Index creation warning (conversations): {e}")
    
    # Create indexes for messages collection
    try:
        database.messages.create_index("conversation_id", name="msg_conversation_id")
        database.messages.create_index("created_at", name="msg_created_at")
    except Exception as e:
        print(f"Index creation warning (messages): {e}")
    
    # Create indexes for career_analyses collection
    try:
        database.career_analyses.create_index("user_id", name="career_user_id")
        database.career_analyses.create_index("created_at", name="career_created_at")
    except Exception as e:
        print(f"Index creation warning (career_analyses): {e}")
    
    # Create indexes for booking_analyses collection
    try:
        database.booking_analyses.create_index("conversation_id", name="booking_conv_id")
        database.booking_analyses.create_index("message_id", name="booking_msg_id")
        database.booking_analyses.create_index("created_at", name="booking_created_at")
    except Exception as e:
        print(f"Index creation warning (booking_analyses): {e}")
    
    # Create indexes for lecturer_availability collection
    try:
        database.lecturer_availability.create_index("lecturer_id", name="lecturer_id_idx")
        database.lecturer_availability.create_index("day_of_week", name="lecturer_day_idx")
        database.lecturer_availability.create_index("is_active", name="lecturer_active_idx")
    except Exception as e:
        print(f"Index creation warning (lecturer_availability): {e}")
    
    # Create indexes for booking_slots collection
    try:
        database.booking_slots.create_index("lecturer_availability_id", name="slot_avail_id")
        database.booking_slots.create_index("user_id", name="slot_user_id")
        database.booking_slots.create_index("booking_date", name="slot_booking_date")
        database.booking_slots.create_index("status", name="slot_status")
    except Exception as e:
        print(f"Index creation warning (booking_slots): {e}") 