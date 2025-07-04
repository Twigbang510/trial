from app.db.session import SessionLocal
from app.models.conversation import Conversation
from app.models.message import Message

def check_messages():
    db = SessionLocal()
    try:
        # Check conversation 51
        conv = db.query(Conversation).filter(Conversation.id == 51).first()
        if conv:
            print(f'Conversation 51: {conv.title}, Status: {conv.booking_status}')
            
            # Check messages for this conversation
            messages = db.query(Message).filter(Message.conversation_id == 51).order_by(Message.created_at.asc()).all()
            print(f'Messages count: {len(messages)}')
            
            for i, msg in enumerate(messages[:5]):  # Show first 5 messages
                print(f'{i+1}. [{msg.sender}]: {msg.content[:50]}...')
                
            # Check if messages have proper data
            if messages:
                first_msg = messages[0]
                print(f'\nFirst message details:')
                print(f'  ID: {first_msg.id}')
                print(f'  Content: {first_msg.content}')
                print(f'  Sender: {first_msg.sender}')
                print(f'  Created: {first_msg.created_at}')
        else:
            print('Conversation 51 not found')
            
        # Also check other conversations with complete status
        complete_convs = db.query(Conversation).filter(Conversation.booking_status == 'complete').all()
        print(f'\nAll complete conversations:')
        for conv in complete_convs:
            msg_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
            print(f'  Conv {conv.id}: {conv.title} - {msg_count} messages')
            
    finally:
        db.close()

if __name__ == "__main__":
    check_messages() 