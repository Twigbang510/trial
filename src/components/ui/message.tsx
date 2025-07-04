import React from 'react';
import { cn } from '@/lib/utils';
import { ChatbotIcon } from '../icons/ChatbotIcon';
import { motion } from 'framer-motion';

export interface MessageProps {
  content: string;
  isBot: boolean;
  timestamp?: Date;
  className?: string;
  variant?: 'default' | 'compact';
}

export const Message: React.FC<MessageProps> = ({
  content,
  isBot,
  timestamp,
  className,
  variant = 'default'
}) => {
  const isCompact = variant === 'compact';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "flex items-end gap-2 animate-fadeIn",
        isBot ? "flex-row" : "flex-row-reverse",
        className
      )}
    >
      {isBot && (
        <div className={cn(
          "flex items-center justify-center fill-green-500",
          isCompact ? "w-8 h-8" : "w-10 h-10"
        )}>
          <ChatbotIcon className={isCompact ? "w-6 h-6" : "w-8 h-8"} />
        </div>
      )}
      
      <div
        className={cn(
          "max-w-[80%] shadow-sm transform transition-all duration-200 hover:shadow-md",
          isCompact ? "px-3 py-2" : "px-5 py-3",
          isBot
            ? "bg-gray-100 text-gray-800 border border-gray-100 rounded-tl-2xl rounded-tr-2xl rounded-br-2xl"
            : "bg-gradient-to-r from-green-500 to-green-600 text-white rounded-tl-2xl rounded-tr-2xl rounded-bl-2xl"
        )}
      >
        <div className={cn("whitespace-pre-wrap", isCompact ? "text-sm" : "text-base")}>
          {content}
        </div>
        {timestamp && (
          <div className={cn(
            "opacity-70 mt-1",
            isCompact ? "text-xs" : "text-xs",
            isBot ? "text-gray-500" : "text-green-100"
          )}>
            {timestamp.toLocaleTimeString('vi-VN', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Loading message component
export const MessageLoading: React.FC<{ className?: string }> = ({ className }) => (
  <div className={cn("flex flex-row items-end gap-2 animate-fadeIn", className)}>
    <div className="w-10 h-10 flex items-center justify-center fill-green-500">
      <ChatbotIcon className="w-8 h-8" />
    </div>
    <div className="max-w-[80%] px-5 py-3 shadow-sm bg-gray-100 text-gray-800 border border-gray-100 rounded-tl-2xl rounded-tr-2xl rounded-br-2xl">
      <div className="flex items-center space-x-1">
        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-150"></span>
        <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse delay-300"></span>
      </div>
    </div>
  </div>
); 