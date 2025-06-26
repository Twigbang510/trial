import axios from "axios";
import { API_URL } from "@/config/app";

const CHATBOT_API_URL = `${API_URL}/api/v1/chatbot`;

interface Message {
  content: string;
  sender: string;
}

interface ChatRequest {
  message: string;
  conversation_id?: number;
  context?: string;
}

interface ChatResponse {
  response: string;
  conversation_id: number;
  is_appropriate: boolean;
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

interface ConversationDetail {
  id: number;
  title: string | null;
  context: string;
  created_at: string;
  updated_at: string | null;
  messages: {
    id: number;
    content: string;
    sender: string;
    is_appropriate: boolean;
    created_at: string;
  }[];
}

const chatbotApi = {
  chat: async (message: string, conversationId?: number, context: string = 'consultant'): Promise<ChatResponse> => {
    try {
      const response = await axios.post<ChatResponse>(`${CHATBOT_API_URL}/chat`, {
        message,
        conversation_id: conversationId,
        context
      });
      return response.data;
    } catch (error) {
      console.error("Error in chatbot API:", error);
      return {
        response: "Sorry, I couldn't process your request. Please try again.",
        conversation_id: conversationId || 0,
        is_appropriate: false
      };
    }
  },

  getConversations: async (): Promise<Conversation[]> => {
    try {
      const response = await axios.get<Conversation[]>(`${CHATBOT_API_URL}/conversations`);
      return response.data;
    } catch (error) {
      console.error("Error fetching conversations:", error);
      return [];
    }
  },

  getConversation: async (conversationId: number): Promise<ConversationDetail | null> => {
    try {
      const response = await axios.get<ConversationDetail>(`${CHATBOT_API_URL}/conversations/${conversationId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching conversation:", error);
      return null;
    }
  },

  deleteConversation: async (conversationId: number): Promise<boolean> => {
    try {
      await axios.delete(`${CHATBOT_API_URL}/conversations/${conversationId}`);
      return true;
    } catch (error) {
      console.error("Error deleting conversation:", error);
      return false;
    }
  },
};

export default chatbotApi;
