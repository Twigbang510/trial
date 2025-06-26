import { useState } from 'react';
import { Mic, Paperclip, ArrowRight, User, Bot } from 'lucide-react';
import { content } from '@/constants/content';
import { motion, AnimatePresence } from 'framer-motion';
import chatbotApi from '@/lib/api/chatbot.api';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatWindowProps {
  activeTab: 'new-chat' | 'career-explorer';
  onConversationChange?: (conversationId: number) => void;
}

// Validation functions
const validateMessage = (message: string): { isValid: boolean; error?: string } => {
  const trimmedMessage = message.trim();
  
  // Check if empty or only whitespace
  if (!trimmedMessage) {
    return { isValid: false, error: "Message cannot be empty" };
  }
  
  // Check if only contains emojis (basic check)
  const emojiRegex = /^[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\s]+$/u;
  if (emojiRegex.test(trimmedMessage)) {
    return { isValid: false, error: "Message cannot contain only emojis" };
  }
  
  // Check if too short (less than 2 characters)
  if (trimmedMessage.length < 2) {
    return { isValid: false, error: "Message must be at least 2 characters" };
  }
  
  // Check if too long (more than 1000 characters)
  if (trimmedMessage.length > 1000) {
    return { isValid: false, error: "Message cannot be more than 1000 characters" };
  }
  
  return { isValid: true };
};

const ChatWindow = ({ activeTab, onConversationChange }: ChatWindowProps) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [validationError, setValidationError] = useState<string>('');
  const [mbtiResult, setMbtiResult] = useState('');
  const [hollandResults, setHollandResults] = useState({
    realistic: '',
    conventional: '',
    investigative: '',
    enterprising: '',
    social: '',
    artistic: ''
  });
  const [hollandSubmit, setHollandSubmit] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState<number | undefined>();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous validation error
    setValidationError('');
    
    // Validate message first
    const validation = validateMessage(message);
    if (!validation.isValid) {
      setValidationError(validation.error!);
      return;
    }
    
    if (isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message.trim(),
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      // Get response from Gemini with conversation storage
      const response = await chatbotApi.chat(message.trim(), currentConversationId, 'consultant');
      
      // Add bot response
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);

      // Update conversation ID if this is a new conversation
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }
    } catch (error) {
      console.error('Error getting bot response:', error);
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I'm having trouble processing your request right now. Please try again.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
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
  };

  const handleHollandSubmit = () => {
    console.log('Holland results submitted:', hollandResults);
    setHollandSubmit(true);
    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: content,
      sender: 'bot',
      timestamp: new Date(),
    };
    return botMessage;
  };

  const handleHollandChange = (type: keyof typeof hollandResults, value: string) => {
    setHollandSubmit(false);
    setHollandResults(prev => ({
      ...prev,
      [type]: value
    }));
  };

  if (activeTab === 'career-explorer') {
    return (
      <div className="flex-1 flex flex-col border-2 border-[#332288] rounded-lg mb-4 h-[calc(100vh-200px)]">
        {/* Messages Area */}
        <div className="flex-1 p-2 md:p-4 overflow-y-auto">
          <div className="flex flex-col items-center md:space-y-4 ">

            {/* Bot's initial question */}
            <div className="flex items-center w-full">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start pl-2 md:pl-4">
                <div className="w-[85%] md:w-[80%] rounded-lg p-3 md:p-4 border-2 border-[#332288] bg-white">
                  <p className="text-xs md:text-sm text-[#332288]">What were your test results?</p>
                </div>
              </div>
            </div>

            {/* Test Results Form */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-center w-full my-4 flex-1"
            >
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                <User className="w-4 h-4 md:w-6 md:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start ml-2 md:ml-4 w-full">
                <div className="rounded-lg bg-white">
                  {/* MBTI Test */}
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.2 }}
                    className="mb-6"
                  >
                    <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-2">MBTI Test*</h3>
                    <input
                      type="text"
                      value={mbtiResult}
                      onChange={(e) => setMbtiResult(e.target.value)}
                      placeholder="Enter your MBTI result (e.g., ESFP)"
                      className="w-[50%] px-3 py-2 border border-[#332288] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-sm md:text-base"
                    />
                  </motion.div>

                  {/* Holland Test */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="w-full"
                  >
                    <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-4">Holland Test*</h3>
                    <div className="flex flex-row gap-4 flex-wrap">
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
                            onChange={(e) => handleHollandChange(type as keyof typeof hollandResults, e.target.value)}
                            placeholder={`Input your score`}
                            className="w-[150px] px-3 py-2 border border-[#332288] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-sm md:text-base"
                          />
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>

            <AnimatePresence>
              {/* Submit Button */}
              {!hollandSubmit && mbtiResult.trim() !== '' && Object.values(hollandResults).every(value => value.trim() !== '') && (
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="flex-1 w-full"
                >
                  <button
                    type="button"
                    className="ml-[calc(8px+2rem)] md:ml-[calc(16px+2.5rem)] px-8 py-3 bg-[#332288] rounded-xl text-white hover:text-gray-200 transition-all duration-300 hover:bg-[#332288]/80 hover:cursor-pointer hover:shadow-lg hover:bg-white hover:text-[#332288] hover:border hover:border-[#332288]"
                    onClick={handleHollandSubmit} 
                  >
                    Submit
                  </button>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Bot's response */}
            <AnimatePresence>
              {hollandSubmit && (
                <motion.div 
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  transition={{ duration: 0.3 }}
                  className="flex items-center w-full"
                >
                  <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                    <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
                  </div>    
                  <div className="flex-1 flex justify-start pl-2 md:pl-4">
                    <div className="w-[85%] md:w-[80%] rounded-lg p-4 border-2 border-[#332288] bg-white">
                      <p className="text-xs md:text-sm text-[#332288]">{content}</p>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

          </div>

        </div>

      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col border-2 border-[#332288] rounded-lg mb-4 h-[calc(100vh-200px)]">
      {/* Messages Area */}
      <div className="flex-1 p-2 md:p-4 overflow-y-auto">
        <div className="flex flex-col items-center space-y-3 md:space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className="flex items-center w-full"
            >
              {msg.sender === 'bot' && (
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                  <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
                </div>
              )}
              <div className={`flex-1 flex ${msg.sender === 'user' ? 'justify-end pr-2 md:pr-4' : 'justify-start pl-2 md:pl-4'}`}>
                <div className={`w-[85%] md:w-[80%] rounded-lg p-3 md:p-4 border-2 border-[#332288] bg-white break-words whitespace-pre-wrap`}>
                  <p className="text-xs md:text-sm text-[#332288]">{msg.content}</p>
                </div>
              </div>
              {msg.sender === 'user' && (
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                  <User className="w-4 h-4 md:w-6 md:h-6 text-white" />
                </div>
              )}
            </div>
          ))}
        
          {/* Loading indicator */}
          {isLoading && (
            <div className="flex items-center w-full">
              <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start pl-2 md:pl-4">
                <div className="w-[85%] md:w-[80%] rounded-lg p-3 md:p-4 border-2 border-[#332288] bg-white">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#332288]"></div>
                    <p className="text-xs md:text-sm text-[#332288]">AI is thinking...</p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-2 md:p-4">   
        <div className="w-full h-16 md:h-20 bg-opacity-30 bg-[#8C8C8C] rounded-full flex items-center gap-1 md:gap-2 p-1 md:px-2">
          {/* File Upload Button */}
          <button
            type="button"
            className="p-1 md:p-2 text-white hover:text-gray-200 transition-colors bg-[#332288] rounded-full"
          >
            <Paperclip className="w-4 h-4 md:w-5 md:h-5" />
          </button>

          {/* Message Input */}
          <input
            type="text"
            value={message}
            onChange={handleInputChange}
            placeholder="Type your prompt here"
            className="flex-1 px-2 md:px-4 py-1 md:py-2 bg-transparent text-[#424242] placeholder-[#424242] focus:outline-none text-sm md:text-base"
            disabled={isLoading}
          />

          {/* Voice Input Button */}
          <button
            type="button"
            className="p-1 md:p-2 text-[#424242] hover:text-gray-200 transition-colors"
            disabled={isLoading}
          >
            <Mic className="w-4 h-4 md:w-5 md:h-5" />
          </button>

          {/* Send Button */}
          <button
            type="submit"
            className="p-2 md:p-4 border-2 bg-[#332288] rounded-full text-white hover:text-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading || !message.trim()}
          >
            <ArrowRight className="w-4 h-4 md:w-5 md:h-5 text-white" />   
          </button>
        </div>
        
        {/* Validation Error */}
        {validationError && (
          <div className="mt-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-600">{validationError}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default ChatWindow; 