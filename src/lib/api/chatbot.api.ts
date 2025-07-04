import { API_URL } from "@/config/app";
import { ChatApiResponse, ConversationApiResponse, EnhancedChatApiResponse } from "@/types/conversation.type";


const CHATBOT_API_URL = `${API_URL}/api/v1/chatbot`;

// Helper function to get auth headers
const getAuthHeaders = (): Record<string, string> => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  };
  
  try {
    const authStateStr = localStorage.getItem('auth_state');
    if (authStateStr) {
      const authState = JSON.parse(authStateStr);
      const token = authState.token;
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
  } catch (error) {
    console.warn('Failed to get auth headers:', error);
  }
  
  return headers;
};

interface Message {
  content: string;
  sender: string;
}

interface ChatRequest {
  message: string;
  conversation_id?: number;
  context?: string;
}

interface Conversation {
  id: number;
  title: string | null;
  context: string;
  booking_status: string;
  created_at: string;
  updated_at: string | null;
  message_count: number;
  last_message: string | null;
}

interface BookingConfirmRequest {
  conversation_id: number;
  availability_id: number;
  lecturer_name: string;
  date: string;
  time: string;
  subject: string;
  location: string;
  duration_minutes: number;
}

const chatbotApi = {
  // Enhanced chat method with booking support
  chat: async (message: string, conversationId?: number, context: string = 'consultant'): Promise<EnhancedChatApiResponse> => {
    try {

      
      const headers = getAuthHeaders();
      
      const requestBody = {
        message,
        conversation_id: conversationId,
        context
      };
      
      const response = await fetch(`${CHATBOT_API_URL}/chat`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody)
      });
      
      
      if (!response.ok) {
        if (response.status === 403) {
          try {
            const errorData = await response.json();
            console.error('403 Error data:', errorData);
            throw new Error(errorData.detail || "Account suspended due to policy violations");
          } catch (parseError) {
            console.error('Failed to parse 403 error:', parseError);
            throw new Error("Account suspended due to policy violations");
          }
        }
        
        // Try to get error text
        try {
          const errorText = await response.text();
          console.error('Error response text:', errorText);
        } catch (textError) {
          console.error('Failed to get error text:', textError);
        }
        
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const responseData = await response.json();

      
      return responseData;
    } catch (error) {
      console.error("=== CHATBOT API ERROR ===");
             console.error("Error type:", error?.constructor?.name);
       console.error("Error message:", (error as Error)?.message);
       console.error("Full error:", error);
      
      // Re-throw if it's a moderation/suspension error
      if (error instanceof Error && error.message.includes("suspended")) {
        console.log('Re-throwing suspension error');
        throw error;
      }
      
      return {
        response: "Sorry, I couldn't process your request. Please try again.",
        conversation_id: conversationId || 0,
        is_appropriate: false,
        moderation_action: 'CLEAN',
        booking_options: [],
        needs_availability_check: false,
        suggested_next_action: 'provide_info'
      };
    }
  },

  // Legacy chat method for backward compatibility
  chatLegacy: async (message: string, conversationId?: number, context: string = 'consultant'): Promise<ChatApiResponse> => {
    const response = await chatbotApi.chat(message, conversationId, context);
    return {
      response: response.response,
      conversation_id: response.conversation_id,
      is_appropriate: response.is_appropriate,
      moderation_action: response.moderation_action as 'CLEAN' | 'WARNING' | 'BLOCKED' | undefined,
      warning_message: response.warning_message
    };
  },

  getConversations: async (): Promise<Conversation[]> => {
    try {
      const response = await fetch(`${CHATBOT_API_URL}/conversations`, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Account suspended");
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error fetching conversations:", error);
      if (error instanceof Error && error.message.includes("suspended")) {
        throw error;
      }
      return [];
    }
  },

  getConversation: async (conversationId: number): Promise<ConversationApiResponse | null> => {
    try {
      const response = await fetch(`${CHATBOT_API_URL}/conversations/${conversationId}`, {
        method: 'GET',
        headers: getAuthHeaders()
      });
      
      if (!response.ok) {
        if (response.status === 403) {
          throw new Error("Account suspended");
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error fetching conversation:", error);
      if (error instanceof Error && error.message.includes("suspended")) {
        throw error;
      }
      return null;
    }
  },

  deleteConversation: async (conversationId: number): Promise<boolean> => {
    try {
      const response = await fetch(`${CHATBOT_API_URL}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers: getAuthHeaders()
      });
      
      if (!response.ok && response.status === 403) {
        throw new Error("Account suspended");
      }
      
      return response.ok;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      if (error instanceof Error && error.message.includes("suspended")) {
        throw error;
      }
      return false;
    }
  },

  // Direct booking confirmation - bypasses AI processing
  confirmBooking: async (bookingData: BookingConfirmRequest): Promise<EnhancedChatApiResponse> => {
    try {

      
      const headers = getAuthHeaders();
      const response = await fetch(`${CHATBOT_API_URL}/confirm-booking`, {
        method: 'POST',
        headers,
        body: JSON.stringify(bookingData)
      });
      
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Booking confirmation error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      return data;
      
    } catch (error) {
      console.error('Booking confirmation failed:', error);
      throw error;
    }
  },

  // Booking cancellation - allows continued chatting
  cancelBooking: async (conversationId: number): Promise<EnhancedChatApiResponse> => {
    try {

      
      const headers = getAuthHeaders();
      const response = await fetch(`${CHATBOT_API_URL}/cancel-booking`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          conversation_id: conversationId,
          message: "No" // This will be saved as user's response
        })
      });
      
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Booking cancellation error:', errorText);
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      return data;
      
    } catch (error) {
      console.error('Booking cancellation failed:', error);
      throw error;
    }
  },

  // Get conversation history
  getConversationHistory: async (conversationId: number) => {
    try {
      const headers = getAuthHeaders();
      const response = await fetch(`${CHATBOT_API_URL}/conversations/${conversationId}`, {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching conversation:', error);
      throw error;
    }
  },

  // Get all conversations
  getConversationsHistory: async (skip: number = 0, limit: number = 100) => {
    try {
      const headers = getAuthHeaders();
      const url = new URL(`${CHATBOT_API_URL}/conversations`);
      url.searchParams.append('skip', skip.toString());
      url.searchParams.append('limit', limit.toString());
      
      const response = await fetch(url.toString(), {
        method: 'GET',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  // Delete conversation
  deleteConversationHistory: async (conversationId: number) => {
    try {
      const headers = getAuthHeaders();
      const response = await fetch(`${CHATBOT_API_URL}/conversations/${conversationId}`, {
        method: 'DELETE',
        headers
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error deleting conversation:', error);
      throw error;
    }
  }
};

export default chatbotApi;
