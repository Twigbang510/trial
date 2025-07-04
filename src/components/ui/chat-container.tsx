import React from 'react';
import { cn } from '@/lib/utils';
import { Message, MessageLoading } from './message';
import { ChatInput } from './chat-input';
import { useChat, ChatMessage } from '@/hooks/useChat';
import { ChatbotIcon } from '../icons/ChatbotIcon';

export interface ChatContainerProps {
  conversationId?: number;
  context?: string;
  className?: string;
  onNewMessage?: (message: ChatMessage) => void;
  onError?: (error: Error) => void;
  placeholder?: string;
  showVoiceButton?: boolean;
  variant?: 'default' | 'compact';
  inputVariant?: 'default' | 'floating' | 'inline';
  emptyStateMessage?: string;
  height?: string;
}

export const ChatContainer: React.FC<ChatContainerProps> = ({
  conversationId,
  context = 'consultant',
  className,
  onNewMessage,
  onError,
  placeholder,
  showVoiceButton = true,
  variant = 'default',
  inputVariant = 'floating',
  emptyStateMessage = "Chưa có tin nhắn nào",
  height = "h-[50vh]"
}) => {
  const { messages, isLoading, sendMessage, containerRef } = useChat({
    conversationId,
    context,
    onNewMessage,
    onError
  });

  const handleVoiceClick = () => {
    // Implement voice input functionality
    console.log('Voice input clicked');
  };

  const EmptyState = () => (
    <div className="flex flex-col items-center justify-center h-full text-gray-500 space-y-4">
      <svg
        className="w-16 h-16 text-gray-300"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
      </svg>
      <p className="text-sm font-medium">{emptyStateMessage}</p>
      <p className="text-xs opacity-75">Hãy bắt đầu cuộc trò chuyện!</p>
    </div>
  );

  return (
    <div className={cn("flex flex-col relative", className)}>
      {/* Chat Header */}
      <div className="fixed top-4 left-0 right-0 z-10 px-5 py-4 border-b flex items-center space-x-2 bg-gradient-to-r from-green-100 to-green-50">
        <div className="w-10 h-10 flex items-center justify-center fill-green-500">
          <ChatbotIcon className="w-8 h-8" />
        </div>
        <div className="flex-1">
          <h2 className="text-xl font-semibold text-gray-800">AIBot</h2>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm font-medium text-green-600">Online</span>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 bg-gradient-to-b h-full pt-24 px-4">
        <div className={cn(height, "overflow-y-auto")} ref={containerRef}>
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <Message
                  key={`message-${index}`}
                  content={message.text}
                  isBot={message.isBot}
                  timestamp={message.timestamp}
                  variant={variant}
                />
              ))}
              
              {isLoading && <MessageLoading />}
              
              <div id="message-anchor" className="h-16" />
            </div>
          )}
        </div>
      </div>

      {/* Chat Input */}
      <ChatInput
        placeholder={placeholder}
        onSubmit={sendMessage}
        disabled={isLoading}
        showVoiceButton={showVoiceButton}
        onVoiceClick={handleVoiceClick}
        variant={inputVariant}
      />
    </div>
  );
};

export default ChatContainer; 