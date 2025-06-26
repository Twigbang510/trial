import google.generativeai as genai
from app.core.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')


def chat_with_gemini(message: str, conversation_history: list = None, context: str = 'consultant') -> str:
    """
    Send a message to Gemini and get response
    """
    try:
        # Create system prompt based on context
        if context == 'consultant':
            system_prompt = """You are a professional career consultant and educational advisor. Your role is to help students and young professionals with:

1. Career guidance and planning
2. University admissions advice
3. Academic counseling
4. Study abroad guidance
5. Personal development and goal setting

Please provide helpful, professional, and accurate advice. Keep responses focused on educational and career topics. If asked about unrelated topics, politely redirect the conversation back to career and educational matters."""
        else:
            system_prompt = """You are a helpful AI assistant. Please provide accurate and helpful responses to user queries."""

        # Prepare conversation context
        if conversation_history:
            # Create chat session with history and system prompt
            chat = model.start_chat(history=conversation_history)
            # Send system prompt first
            chat.send_message(system_prompt)
            response = chat.send_message(message)
        else:
            # Single message with system prompt
            full_prompt = f"{system_prompt}\n\nUser: {message}"
            response = model.generate_content(full_prompt)
        
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again later."

def format_conversation_history(messages: list) -> list:
    """
    Format conversation history for Gemini API
    """
    formatted_history = []
    for msg in messages:
        if msg['sender'] == 'user':
            formatted_history.append({
                'role': 'user',
                'parts': [msg['content']]
            })
        elif msg['sender'] == 'bot':
            formatted_history.append({
                'role': 'model',
                'parts': [msg['content']]
            })
    return formatted_history 