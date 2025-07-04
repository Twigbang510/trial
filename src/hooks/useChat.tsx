import { useState, useCallback, useRef, useEffect } from 'react';
import chatbotApi from '@/lib/api/chatbot.api';

export interface ChatMessage {
  text: string;
  isBot: boolean;
  timestamp?: Date;
}

export interface UseChatOptions {
  conversationId?: number;
  context?: string;
  onError?: (error: Error) => void;
  onNewMessage?: (message: ChatMessage) => void;
  autoScroll?: boolean;
}

export const useChat = (options: UseChatOptions = {}) => {
  const {
    conversationId,
    context = 'consultant',
    onError,
    onNewMessage,
    autoScroll = true
  } = options;

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [clientId, setClientId] = useState<string>();
  const containerRef = useRef<HTMLDivElement>(null);

  // Generate client ID
  const generateClientId = useCallback(() => {
    if (clientId) return clientId;
    const id = `client_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setClientId(id);
    return id;
  }, [clientId]);

  // Auto scroll to bottom
  const scrollToBottom = useCallback(() => {
    if (autoScroll && containerRef.current) {
      const lastMessage = containerRef.current.lastElementChild?.lastElementChild;
      lastMessage?.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [autoScroll]);

  // Send message
  const sendMessage = useCallback(async (messageText: string) => {
    if (!messageText.trim() || isLoading) return;

    if (!clientId) {
      generateClientId();
    }

    const userMessage: ChatMessage = {
      text: messageText,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatbotApi.chat(messageText, conversationId, context);

      const botMessage: ChatMessage = {
        text: response.response,
        isBot: true,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
      
      if (onNewMessage) {
        onNewMessage(botMessage);
      }

      return response;
    } catch (error) {
      const errorMessage: ChatMessage = {
        text: "Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.",
        isBot: true,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
      
      if (onError) {
        onError(error as Error);
      }
    } finally {
      setIsLoading(false);
    }
  }, [clientId, conversationId, context, isLoading, onError, onNewMessage, generateClientId]);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Load conversation history
  const loadConversation = useCallback(async (convId: number) => {
    try {
      setIsLoading(true);
      // Implement conversation loading logic here
      // const conversation = await chatbotApi.getConversation(convId);
      // setMessages(conversation.messages.map(...));
    } catch (error) {
      if (onError) {
        onError(error as Error);
      }
    } finally {
      setIsLoading(false);
    }
  }, [onError]);

  // Auto scroll effect
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Initialize client ID
  useEffect(() => {
    generateClientId();
  }, [generateClientId]);

  return {
    messages,
    isLoading,
    sendMessage,
    clearMessages,
    loadConversation,
    containerRef,
    scrollToBottom,
    clientId
  };
}; 