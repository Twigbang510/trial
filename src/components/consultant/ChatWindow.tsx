import { useState } from 'react';
import { Mic, Paperclip, ArrowRight, User, Bot } from 'lucide-react';
import { content } from '@/constants/content';
import { motion, AnimatePresence } from 'framer-motion';
import chatbotApi from '@/lib/api/chatbot.api';
import BookingOptions from '@/components/BookingOptions';
import ConfirmationButtons from '@/components/ConfirmationButtons';
import { BookingOption } from '@/types/conversation.type';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  bookingOptions?: BookingOption[];
  warningMessage?: string;
  awaitingConfirmation?: {
    option: BookingOption;
    confirmationText: string;
  };
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
    
    console.log('=== CHAT SUBMIT DEBUG ===');
    console.log('Message:', message);
    
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
      // Get enhanced response with booking options
      const response = await chatbotApi.chat(message.trim(), currentConversationId, 'consultant');
      
      // Debug: Log the response to check booking_options
      console.log('Chat response:', response);
      console.log('Booking options received:', response.booking_options);
      
      // Add bot response with booking options
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
        bookingOptions: response.booking_options || [],
        warningMessage: response.warning_message
      };
      console.log('=== BOT MESSAGE CREATED ===');
      console.log('Bot message:', botMessage);
      console.log('Bot message bookingOptions:', botMessage.bookingOptions);
      console.log('Bot message bookingOptions length:', botMessage.bookingOptions?.length);
      setMessages(prev => [...prev, botMessage]);

      // Update conversation ID if this is a new conversation
      if (!currentConversationId && response.conversation_id) {
        setCurrentConversationId(response.conversation_id);
        onConversationChange?.(response.conversation_id);
      }
    } catch (error) {
      console.error('=== CHAT API ERROR ===');
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

  const handleBookingOptionSelect = (option: BookingOption) => {
    // Create confirmation message from bot
    const confirmationText = `Do you want to confirm booking with **${option.lecturer_name}** on **${option.date}** at **${option.time}** for **${option.subject}**?\n\n📍 **Location:** ${option.location}\n⏱️ **Duration:** ${option.duration_minutes} minutes`;
    
    const confirmationMessage: Message = {
      id: Date.now().toString(),
      content: confirmationText,
      sender: 'bot',
      timestamp: new Date(),
      awaitingConfirmation: {
        option,
        confirmationText
      }
    };
    
    setMessages(prev => [...prev, confirmationMessage]);
  };

  const handleConfirmBooking = async (option: BookingOption) => {
    // Add user's "Yes" response
    const userYesMessage: Message = {
      id: Date.now().toString(),
      content: "Yes",
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userYesMessage]);
    setIsLoading(true);

    try {
      // Send confirmation to backend
      const confirmationMessage = `Yes, I confirm booking with ${option.lecturer_name} on ${option.date} at ${option.time} for ${option.subject}.`;
      const response = await chatbotApi.chat(confirmationMessage, currentConversationId, 'consultant');
      
      // Add success response
      const successMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response || `✅ Great! Your booking with ${option.lecturer_name} on ${option.date} at ${option.time} for ${option.subject} has been confirmed. You will receive an email confirmation soon.`,
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, successMessage]);
    } catch (error) {
      console.error('Error confirming booking:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, there was an error confirming your booking. Please try again.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelBooking = () => {
    // Add user's "No" response
    const userNoMessage: Message = {
      id: Date.now().toString(),
      content: "No",
      sender: 'user',
      timestamp: new Date(),
    };
    
    // Add bot's response to continue
    const continueMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: "No problem! I can help you find another time or answer any more questions about booking. Do you need any more help?",
      sender: 'bot',
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userNoMessage, continueMessage]);
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

                  {/* Holland Code Test */}
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="mb-6"
                  >
                    <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-2">Holland Code Test*</h3>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { key: 'realistic', label: 'Realistic' },
                        { key: 'investigative', label: 'Investigative' },
                        { key: 'artistic', label: 'Artistic' },
                        { key: 'social', label: 'Social' },
                        { key: 'enterprising', label: 'Enterprising' },
                        { key: 'conventional', label: 'Conventional' }
                      ].map(({ key, label }) => (
                        <div key={key} className="flex flex-col">
                          <label className="text-xs text-[#332288] mb-1">{label}</label>
                          <input
                            type="text"
                            value={hollandResults[key as keyof typeof hollandResults]}
                            onChange={(e) => handleHollandChange(key as keyof typeof hollandResults, e.target.value)}
                            placeholder="Score"
                            className="px-2 py-1 border border-[#332288] rounded focus:outline-none focus:ring-1 focus:ring-[#332288] bg-white text-black text-xs md:text-sm"
                          />
                        </div>
                      ))}
                    </div>
                  </motion.div>

                  {/* Submit Button */}
                  <motion.button
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.6 }}
                    onClick={handleHollandSubmit}
                    className="w-full py-2 px-4 bg-[#332288] text-white rounded-lg hover:bg-[#2a1a70] transition-colors text-sm md:text-base"
                  >
                    Submit Test Results
                  </motion.button>
                </div>
              </div>
            </motion.div>

            {/* Results Display */}
            {hollandSubmit && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="flex items-center w-full mt-4"
              >
                <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center">
                  <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
                </div>
                <div className="flex-1 flex justify-start pl-2 md:pl-4">
                  <div className="w-[85%] md:w-[80%] rounded-lg p-3 md:p-4 border-2 border-[#332288] bg-white">
                    <div className="text-xs md:text-sm text-[#332288] whitespace-pre-line">
                      {content}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Default new-chat tab
  return (
    <div className="flex-1 flex flex-col border-2 border-[#332288] rounded-lg mb-4 h-[calc(100vh-200px)]">
      {/* Messages Area */}
      <div className="flex-1 p-2 md:p-4 overflow-y-auto">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex items-start mb-4 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div className={`flex items-start max-w-[85%] md:max-w-[80%] ${
                msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
              }`}>
                {/* Avatar */}
                <div className={`w-8 h-8 md:w-10 md:h-10 rounded-full flex items-center justify-center ${
                  msg.sender === 'user' 
                    ? 'bg-blue-500 ml-2 md:ml-4' 
                    : 'bg-[#332288] mr-2 md:mr-4'
                }`}>
                  {msg.sender === 'user' ? (
                    <User className="w-4 h-4 md:w-6 md:h-6 text-white" />
                  ) : (
                    <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
                  )}
                </div>

                {/* Message Content */}
                <div className="flex-1">
                  <div className={`rounded-lg p-3 md:p-4 ${
                    msg.sender === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'border-2 border-[#332288] bg-white text-[#332288]'
                  }`}>
                                      <p className="text-xs md:text-sm whitespace-pre-wrap">{msg.content}</p>
                  
                  {/* Debug booking options */}
                  {(() => {
                    console.log('=== RENDER CHECK ===', {
                      msgId: msg.id,
                      hasBookingOptions: !!msg.bookingOptions,
                      bookingOptionsLength: msg.bookingOptions?.length,
                      bookingOptions: msg.bookingOptions
                    });
                    return null;
                  })()}
                  
                  {msg.bookingOptions && msg.bookingOptions.length > 0 && (() => {
                    console.log('✅ RENDERING BookingOptions with:', msg.bookingOptions);
                    return <BookingOptions options={msg.bookingOptions} onOptionSelect={handleBookingOptionSelect} />;
                  })()}
                  </div>

                  {/* Warning Message */}
                  {msg.warningMessage && (
                    <div className="mt-2 p-2 bg-yellow-100 border border-yellow-400 rounded-lg">
                      <p className="text-xs text-yellow-800">{msg.warningMessage}</p>
                    </div>
                  )}

                  {/* Confirmation Buttons */}
                  {msg.awaitingConfirmation && (
                    <div className="mt-4 flex justify-center">
                      <ConfirmationButtons
                        onConfirm={() => handleConfirmBooking(msg.awaitingConfirmation!.option)}
                        onCancel={handleCancelBooking}
                        confirmText="Yes"
                        cancelText="No"
                      />
                    </div>
                  )}

                  {/* Timestamp */}
                  <p className="text-xs text-gray-500 mt-1">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-start justify-start mb-4"
          >
            <div className="w-8 h-8 md:w-10 md:h-10 rounded-full bg-[#332288] flex items-center justify-center mr-2 md:mr-4">
              <Bot className="w-4 h-4 md:w-6 md:h-6 text-white" />
            </div>
            <div className="rounded-lg p-3 md:p-4 border-2 border-[#332288] bg-white">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-[#332288] rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-[#332288] rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-[#332288] rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t-2 border-[#332288] p-2 md:p-4">
        {validationError && (
          <div className="mb-2 p-2 bg-red-100 border border-red-400 rounded-lg">
            <p className="text-xs text-red-800">{validationError}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex items-center space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={handleInputChange}
              placeholder="Ask me anything about your career..."
              className="w-full px-3 md:px-4 py-2 md:py-3 border-2 border-[#332288] rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] text-xs md:text-sm"
              disabled={isLoading}
            />
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              type="button"
              className="p-2 text-[#332288] hover:bg-[#332288] hover:text-white rounded-lg transition-colors"
              disabled={isLoading}
            >
              <Paperclip className="w-4 h-4 md:w-5 md:h-5" />
            </button>
            
            <button
              type="button"
              className="p-2 text-[#332288] hover:bg-[#332288] hover:text-white rounded-lg transition-colors"
              disabled={isLoading}
            >
              <Mic className="w-4 h-4 md:w-5 md:h-5" />
            </button>
            
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="p-2 bg-[#332288] text-white rounded-lg hover:bg-[#2a1a70] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowRight className="w-4 h-4 md:w-5 md:h-5" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow; 