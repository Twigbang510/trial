import { useState, useRef, useEffect } from 'react';
import { Mic, Paperclip, ArrowRight, User, Bot, MessageSquare, Send } from 'lucide-react';
import { motion } from 'framer-motion';
import chatbotApi from '@/lib/api/chatbot.api';
import { ChatTab, MessageType } from '@/types/conversation.type';

interface ChatWindowTabsProps {
  activeTab: ChatTab;
  onAddMessage: (tabId: string, message: MessageType) => void;
  onConversationChange?: (conversationId: number) => void;
  onUpdateTabConversationId?: (tabId: string, conversationId: number) => void;
  canCreateNewChat: boolean;
  onCreateNewTab: () => string;
  onRefreshUserData: () => Promise<void>;
}

// Validation function with better logic including emoji detection
const validateMessage = (message: string): { isValid: boolean; error?: string } => {
  const trimmedMessage = message.trim();
  
  // Check if message is empty
  if (!trimmedMessage) {
    return { isValid: false, error: "Please enter a message" };
  }
  
  // Check minimum length
  if (trimmedMessage.length < 2) {
    return { isValid: false, error: "Message must be at least 2 characters long" };
  }
  
  // Check maximum length
  if (trimmedMessage.length > 1000) {
    return { isValid: false, error: "Message must be less than 1000 characters" };
  }
  
  // Enhanced emoji detection
  const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F900}-\u{1F9FF}]|[\u{1F018}-\u{1F270}]/gu;
  const emojiMatches = trimmedMessage.match(emojiRegex) || [];
  const textWithoutEmoji = trimmedMessage.replace(emojiRegex, '').trim();
  
  // Check if message contains only emojis (no meaningful text)
  if (emojiMatches.length > 0 && textWithoutEmoji.length === 0) {
    return { isValid: false, error: "Please include text along with emojis" };
  }
  
  // Check if message has too many emojis
  if (emojiMatches.length > 10) {
    return { isValid: false, error: "Please use fewer emojis in your message" };
  }
  
  // Check for spam patterns (repeated characters)
  const repeatedCharPattern = /(.)\1{10,}/;
  if (repeatedCharPattern.test(trimmedMessage)) {
    return { isValid: false, error: "Please avoid excessive repeated characters" };
  }
  
  // Check for inappropriate content (basic patterns)
  const inappropriatePatterns = [
    /fuck|shit|damn|hell|ass/i,
    /spam|test{3,}|hello{3,}/i
  ];
  
  for (const pattern of inappropriatePatterns) {
    if (pattern.test(trimmedMessage)) {
      return { isValid: false, error: "Please keep your message appropriate and professional" };
    }
  }
  
  return { isValid: true };
};

// Real-time validation as user types
const validateMessageRealTime = (message: string): { showWarning: boolean; warning?: string } => {
  const trimmedMessage = message.trim();
  
  if (trimmedMessage.length > 800) {
    return { showWarning: true, warning: `${1000 - trimmedMessage.length} characters remaining` };
  }
  
  if (trimmedMessage.length > 0 && trimmedMessage.length < 2) {
    return { showWarning: true, warning: "Message too short" };
  }
  
  // Check emoji count in real-time
  const emojiRegex = /[\u{1F600}-\u{1F64F}]|[\u{1F300}-\u{1F5FF}]|[\u{1F680}-\u{1F6FF}]|[\u{1F1E0}-\u{1F1FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F900}-\u{1F9FF}]|[\u{1F018}-\u{1F270}]/gu;
  const emojiMatches = trimmedMessage.match(emojiRegex) || [];
  
  if (emojiMatches.length > 8) {
    return { showWarning: true, warning: "Too many emojis" };
  }
  
  return { showWarning: false };
};

const ChatWindowTabs = ({ activeTab, onAddMessage, onConversationChange, onUpdateTabConversationId, canCreateNewChat, onCreateNewTab, onRefreshUserData }: ChatWindowTabsProps) => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState('');
  const [validationWarning, setValidationWarning] = useState('');
  const [moderationWarning, setModerationWarning] = useState('');
  const [isBlocked, setIsBlocked] = useState(false);
  const [mbtiResult, setMbtiResult] = useState('');
  const [hollandResults, setHollandResults] = useState({
    realistic: '',
    investigative: '',
    artistic: '',
    social: '',
    enterprising: '',
    conventional: ''
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeTab.messages]);

  const handleSendMessage = async () => {
    // Check if chat is blocked
    if (isBlocked) {
      setValidationError('This conversation has been blocked due to policy violations.');
      return;
    }

    // Validate message before sending
    const validation = validateMessage(message);
    if (!validation.isValid) {
      setValidationError(validation.error || 'Invalid message');
      return;
    }

    // Clear any existing errors/warnings
    setValidationError('');
    setValidationWarning('');
    setModerationWarning('');

    const userMessage: MessageType = {
      id: Date.now().toString(),
      content: message.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    // If this is new-chat tab, create a new conversation tab first
    let targetTabId = activeTab.id;
    let conversationId = activeTab.conversationId;

    if (activeTab.type === 'new-chat') {
      // Create new conversation tab
      targetTabId = onCreateNewTab();
      conversationId = undefined; // Will be created by API
    }

    // Add user message to the target tab
    onAddMessage(targetTabId, userMessage);
    setMessage('');
    setIsLoading(true);

    try {
      // Call chatbot API
      const context = activeTab.type === 'career-explorer' ? 'consultant' : 'consultant';
      const response = await chatbotApi.chat(userMessage.content, conversationId, context);
      
      // Handle moderation responses
      if (response.moderation_action === 'BLOCKED') {
        setIsBlocked(true);
        setModerationWarning(response.warning_message || 'Conversation blocked due to policy violations.');
        
        // Add system message about blocking
        const systemMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          content: response.response,
          sender: 'bot',
          timestamp: new Date(),
          isAppropriate: false
        };
        onAddMessage(targetTabId, systemMessage);
        
      } else {
        // Handle warning or clean responses
        if (response.moderation_action === 'WARNING' && response.warning_message) {
          setModerationWarning(response.warning_message);
          
          // Refresh user data to update violation count immediately
          try {
            await onRefreshUserData();
          } catch (refreshError) {
            console.error('Failed to refresh user data after warning:', refreshError);
          }
        }
        
        // Add bot response to the target tab
        const botMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          content: response.response,
          sender: 'bot',
          timestamp: new Date(),
          isAppropriate: response.is_appropriate
        };

        onAddMessage(targetTabId, botMessage);
      }

      // Update conversation ID if this was a new conversation
      if (response.conversation_id && response.conversation_id > 0) {
        // If this was a new chat tab that created a conversation, update the tab ID
        if (activeTab.type === 'new-chat' && onUpdateTabConversationId) {
          onUpdateTabConversationId(targetTabId, response.conversation_id);
        }
        
        if (onConversationChange) {
          onConversationChange(response.conversation_id);
        }
      }

    } catch (error) {
      console.error('Error getting bot response:', error);
      
      // Handle account suspension
      if (error instanceof Error && error.message.includes('suspended')) {
        setIsBlocked(true);
        setModerationWarning('Your account has been suspended due to policy violations. Please contact support.');
        
        try {
          await onRefreshUserData();
        } catch (refreshError) {
          console.error('Failed to refresh user data after suspension:', refreshError);
        }
        
        const suspensionMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          content: 'Account suspended due to policy violations. Please contact support to restore access.',
          sender: 'bot',
          timestamp: new Date(),
          isAppropriate: false
        };
        onAddMessage(targetTabId, suspensionMessage);
      } else {
        const errorMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          content: 'Sorry, I encountered an error. Please try again.',
          sender: 'bot',
          timestamp: new Date()
        };
        onAddMessage(targetTabId, errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setMessage(newValue);
    
    // Clear validation error when user starts typing
    if (validationError) {
      setValidationError('');
    }
    
    // Real-time validation warnings
    const realtimeValidation = validateMessageRealTime(newValue);
    setValidationWarning(realtimeValidation.showWarning ? realtimeValidation.warning || '' : '');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage();
  };

  // Check if input should be disabled
  const isInputDisabled = activeTab.type === 'new-chat' && !canCreateNewChat;

  // Career Explorer Tab
  if (activeTab.type === 'career-explorer') {
    return (
      <div className="flex-1 flex flex-col border-2 border-[#332288] rounded-lg h-[calc(100vh-180px)] md:h-[calc(100vh-200px)]">
        <div className="flex-1 p-2 md:p-4 overflow-y-auto">
          <div className="flex flex-col items-center space-y-3 md:space-y-4">
            {/* Bot's initial question */}
            <div className="flex items-center w-full">
              <div className="w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                <Bot className="w-3 h-3 md:w-4 md:h-4 lg:w-6 lg:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start pl-2 md:pl-4">
                <div className="w-[90%] md:w-[85%] lg:w-[80%] rounded-lg p-2 md:p-3 lg:p-4 border-2 border-[#332288] bg-white">
                  <p className="text-xs md:text-sm text-[#332288]">What were your test results?</p>
                </div>
              </div>
            </div>

            {/* Test Results Form */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-center w-full my-2 md:my-4 flex-1"
            >
              <div className="w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                <User className="w-3 h-3 md:w-4 md:h-4 lg:w-6 lg:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start ml-2 md:ml-4 w-full">
                <div className="rounded-lg bg-white w-full">
                  {/* MBTI Test */}
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="mb-4 md:mb-6"
                  >
                    <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-2">MBTI Test*</h3>
                    <input
                      type="text"
                      value={mbtiResult}
                      onChange={(e) => setMbtiResult(e.target.value)}
                      placeholder="Enter your MBTI result (e.g., ESFP)"
                      className="w-full md:w-[70%] lg:w-[50%] px-3 py-2 border border-[#332288] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-xs md:text-sm lg:text-base"
                    />
                  </motion.div>

                  {/* Holland Test */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="w-full"
                  >
                    <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-3 md:mb-4">Holland Test*</h3>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:flex lg:flex-row gap-2 md:gap-4 flex-wrap">
                      {Object.entries(hollandResults).map(([type, value], index) => (
                        <motion.div 
                          key={type} 
                          className="relative"
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: 0.4 + index * 0.1 }}
                        >
                          <span className="absolute -top-2 left-2 bg-white px-1 text-xs text-[#332288]">
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </span>
                          <input
                            type="text"
                            value={value}
                            onChange={(e) => setHollandResults(prev => ({
                              ...prev,
                              [type]: e.target.value
                            }))}
                            placeholder="Score"
                            className="w-full md:w-[120px] lg:w-[150px] px-2 md:px-3 py-2 border border-[#332288] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-xs md:text-sm lg:text-base"
                          />
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    );
  }

  // Chat Tab (new-chat or conversation)
  return (
    <div className="flex-1 flex flex-col border-2 border-[#332288] rounded-lg h-[calc(100vh-180px)] md:h-[calc(100vh-200px)]">
      {/* Messages Area */}
      <div className="flex-1 p-2 md:p-4 overflow-y-auto">
        <div className="flex flex-col space-y-3 md:space-y-4">
          {activeTab.messages.length === 0 && (
            <div className="text-center text-gray-500 mt-4 md:mt-8">
              {activeTab.type === 'new-chat' ? (
                <>
                  <MessageSquare className="w-8 h-8 md:w-12 md:h-12 mx-auto mb-3 md:mb-4 text-gray-300" />
                  <p className="text-base md:text-lg font-medium text-gray-600 mb-2">Ready to start a new conversation?</p>
                  <p className="text-xs md:text-sm px-4">
                    {canCreateNewChat 
                      ? "Type your message below and I'll help you with education and career guidance."
                      : "Please complete your schedule to start chatting."
                    }
                  </p>
                </>
              ) : (
                <>
                  <p className="text-sm md:text-base">Start a conversation by typing a message below.</p>
                  <p className="text-xs md:text-sm mt-2 px-4">Ask me anything about education, career guidance, or university information.</p>
                </>
              )}
            </div>
          )}
          
          {activeTab.messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start gap-2 md:gap-3 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'bot' && (
                <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-[#332288] flex items-center justify-center flex-shrink-0">
                  <Bot className="w-3 h-3 md:w-4 md:h-4 text-white" />
                </div>
              )}
              
              <div
                className={`max-w-[85%] md:max-w-[80%] rounded-lg p-2 md:p-3 ${
                  msg.sender === 'user'
                    ? 'bg-[#332288] text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-xs md:text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {msg.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </p>
              </div>
              
              {msg.sender === 'user' && (
                <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-[#332288] flex items-center justify-center flex-shrink-0">
                  <User className="w-3 h-3 md:w-4 md:h-4 text-white" />
                </div>
              )}
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-start gap-2 md:gap-3">
              <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-[#332288] flex items-center justify-center">
                <Bot className="w-3 h-3 md:w-4 md:h-4 text-white" />
              </div>
              <div className="bg-gray-100 rounded-lg p-2 md:p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-[#332288] p-3 md:p-4 bg-gray-50">
        {/* Character count and warnings */}
        {(validationWarning || validationError || moderationWarning) && (
          <div className="mb-2 md:mb-3 space-y-2">
            {validationError && (
              <div className="p-2 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <p className="text-xs md:text-sm text-red-600">{validationError}</p>
                </div>
              </div>
            )}
            {validationWarning && !validationError && (
              <div className="p-2 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <p className="text-xs md:text-sm text-yellow-600">{validationWarning}</p>
                </div>
              </div>
            )}
            {moderationWarning && (
              <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  <p className="text-xs md:text-sm text-orange-700 font-medium">{moderationWarning}</p>
                </div>
              </div>
            )}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2 md:gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={handleInputChange}
              placeholder={isInputDisabled || isBlocked ? "Chat is currently disabled" : "Type your message here..."}
              className={`w-full px-3 md:px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] focus:border-transparent text-sm text-black md:text-base transition-all duration-200 ${
                isInputDisabled || isBlocked
                  ? 'bg-gray-100 border-gray-300 text-black cursor-not-allowed' 
                  : validationError
                  ? 'bg-white border-red-300 focus:ring-red-400'
                  : validationWarning
                  ? 'bg-white border-yellow-300 focus:ring-yellow-400'
                  : moderationWarning
                  ? 'bg-white border-orange-300 focus:ring-orange-400'
                  : 'bg-white border-gray-300'
              }`}
              disabled={isInputDisabled || isLoading || isBlocked}
              maxLength={1000}
            />
            
            {/* Character count */}
            {message.length > 0 && (
              <div className="absolute -bottom-5 right-0 text-xs text-gray-400">
                {message.length}/1000
              </div>
            )}
          </div>
          
          <button
            type="submit"
            disabled={!message.trim() || isLoading || isInputDisabled || !!validationError || isBlocked}
            className={`px-3 md:px-4 py-2 rounded-lg font-medium transition-all duration-200 text-sm md:text-base ${
              !message.trim() || isLoading || isInputDisabled || !!validationError || isBlocked
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-[#332288] text-white hover:bg-[#2a1f70] shadow-md hover:shadow-lg'
            }`}
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 md:w-4 md:h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span className="hidden md:inline">Sending...</span>
              </div>
            ) : (
              <Send className="w-4 h-4 md:w-5 md:h-5" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindowTabs; 