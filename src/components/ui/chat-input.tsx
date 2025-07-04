import React, { useState, KeyboardEvent } from 'react';
import { cn } from '@/lib/utils';
import { Mic, SendHorizonal } from 'lucide-react';

export interface ChatInputProps {
  placeholder?: string;
  onSubmit: (message: string) => void;
  disabled?: boolean;
  showVoiceButton?: boolean;
  onVoiceClick?: () => void;
  className?: string;
  variant?: 'default' | 'floating' | 'inline';
}

export const ChatInput: React.FC<ChatInputProps> = ({
  placeholder = "Nhập câu hỏi của bạn...",
  onSubmit,
  disabled = false,
  showVoiceButton = true,
  onVoiceClick,
  className,
  variant = 'default'
}) => {
  const [inputValue, setInputValue] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || disabled) return;
    
    onSubmit(inputValue.trim());
    setInputValue("");
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const getContainerStyles = () => {
    switch (variant) {
      case 'floating':
        return "fixed bottom-0 left-0 right-0 z-10 bg-transparent";
      case 'inline':
        return "w-full bg-white border border-gray-200 rounded-lg";
      default:
        return "w-full bg-white rounded-full shadow-[0_3px_10px_rgb(0,0,0,0.2)]";
    }
  };

  const getInputContainerStyles = () => {
    switch (variant) {
      case 'floating':
        return "px-5 py-4";
      case 'inline':
        return "p-2";
      default:
        return "p-2";
    }
  };

  const getInputFieldStyles = () => {
    switch (variant) {
      case 'inline':
        return "flex-1 border-none px-3 py-2 text-sm focus:outline-none placeholder:text-gray-400 bg-transparent";
      default:
        return "flex-1 bg-transparent border-none px-3 py-2 text-sm focus:outline-none placeholder:text-gray-400";
    }
  };

  return (
    <div className={cn(getContainerStyles(), className)}>
      <form onSubmit={handleSubmit} className={getInputContainerStyles()}>
        <div className={cn(
          "flex gap-3 items-center",
          variant === 'floating' && "bg-white rounded-full p-2 shadow-[0_3px_10px_rgb(0,0,0,0.2)]",
          variant === 'inline' && "bg-gray-50 rounded-lg"
        )}>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            className={getInputFieldStyles()}
            placeholder={placeholder}
            disabled={disabled}
          />

          <div className="flex flex-row justify-center items-center space-x-2 mr-2">
            {showVoiceButton && (
              <button
                type="button"
                onClick={onVoiceClick}
                disabled={disabled}
                className={cn(
                  "hover:text-green-500 transition-colors duration-200 bg-transparent",
                  disabled && "opacity-50 cursor-not-allowed"
                )}
                aria-label="Voice input"
              >
                <Mic
                  width={24}
                  height={24}
                  className="stroke-1 hover:stroke-2 transition-all"
                />
              </button>
            )}

            <button
              type="submit"
              disabled={disabled || !inputValue.trim()}
              className={cn(
                "bg-green-500 hover:bg-green-600 text-white rounded-full p-2 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-300",
                (disabled || !inputValue.trim()) && "opacity-50 cursor-not-allowed"
              )}
              aria-label="Send message"
            >
              <SendHorizonal width={20} height={20} />
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default ChatInput; 