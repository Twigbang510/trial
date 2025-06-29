import { API_URL } from "@/config/app";
import { ChatApiResponse, ConversationApiResponse } from "@/types/conversation.type";

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
  created_at: string;
  updated_at: string | null;
  message_count: number;
  last_message: string | null;
}

const chatbotApi = {
  chat: async (message: string, conversationId?: number, context: string = 'consultant'): Promise<ChatApiResponse> => {
    try {
      const response = await fetch(`${CHATBOT_API_URL}/chat`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          message,
          conversation_id: conversationId,
          context
        })
      });
      
      if (!response.ok) {
        if (response.status === 403) {
          const errorData = await response.json();
          throw new Error(errorData.detail || "Account suspended due to policy violations");
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error("Error in chatbot API:", error);
      
      // Re-throw if it's a moderation/suspension error
      if (error instanceof Error && error.message.includes("suspended")) {
        throw error;
      }
      
      return {
        response: "Sorry, I couldn't process your request. Please try again.",
        conversation_id: conversationId || 0,
        is_appropriate: false,
        moderation_action: 'CLEAN'
      };
    }
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
};

export default chatbotApi;
