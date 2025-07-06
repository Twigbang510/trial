import { useState, useRef, useEffect } from 'react';
import { User, Bot, MessageSquare, Send } from 'lucide-react';
import { motion } from 'framer-motion';
import chatbotApi from '@/lib/api/chatbot.api';
import careerAnalysisApi, { type CareerAnalysisResponse } from '@/lib/api/career-analysis.api';
import { ChatTab, MessageType, BookingOption } from '@/types/conversation.type';
import BookingOptions from '@/components/BookingOptions';
import ConfirmationButtons from '@/components/ConfirmationButtons';
import BookingSuccessModal from '@/components/BookingSuccessModal';

interface ChatWindowTabsProps {
  activeTab: ChatTab;
  tabs?: ChatTab[];
  onAddMessage: (tabId: string, message: MessageType) => void;
  onConversationChange?: (conversationId: number) => void;
  onUpdateTabConversationId?: (tabId: string, conversationId: number) => void;
  updateTabBookingStatus?: (tabId: string, status: string) => void;
  canCreateNewChat: boolean;
  onCreateNewTab: () => string;
  onRefreshUserData: () => Promise<void>;
}

// Validation functions
const validateMessage = (message: string): { isValid: boolean; error?: string } => {
  const trimmedMessage = message.trim();
  
  if (!trimmedMessage) {
    return { isValid: false, error: "Message cannot be empty" };
  }
  
  const emojiRegex = /^[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\s]+$/u;
  if (emojiRegex.test(trimmedMessage)) {
    return { isValid: false, error: "Message cannot contain only emojis" };
  }
  
  if (trimmedMessage.length < 2) {
    return { isValid: false, error: "Message must be at least 2 characters" };
  }
  
  if (trimmedMessage.length > 1000) {
    return { isValid: false, error: "Message cannot be more than 1000 characters" };
  }
  
  return { isValid: true };
};

const validateMessageRealTime = (message: string): { showWarning: boolean; warning?: string } => {
  const trimmedMessage = message.trim();
  
  if (trimmedMessage.length > 800) {
    return { showWarning: true, warning: `Characters: ${trimmedMessage.length}/1000 - Approaching limit` };
  }
  
  if (trimmedMessage.length > 900) {
    return { showWarning: true, warning: `Characters: ${trimmedMessage.length}/1000 - Close to limit` };
  }
  
  return { showWarning: false };
};

const ChatWindowTabs = ({ activeTab, tabs, onAddMessage, onConversationChange, onUpdateTabConversationId, updateTabBookingStatus, canCreateNewChat, onCreateNewTab, onRefreshUserData }: ChatWindowTabsProps) => {
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
  
  // Career Explorer specific states
  const [careerAnalysis, setCareerAnalysis] = useState<{
    isAnalyzing: boolean;
    results: CareerAnalysisResponse | null;
    error: string | null;
  }>({
    isAnalyzing: false,
    results: null,
    error: null
  });
  
  const [careerFormErrors, setCareerFormErrors] = useState({
    mbti: '',
    holland: ''
  });

  const [confirmationProcessing, setConfirmationProcessing] = useState<string | null>(null);
  const [bookingSuccessModal, setBookingSuccessModal] = useState<{
    isOpen: boolean;
    bookingDetails: any;
    emailSent: boolean;
  }>({
    isOpen: false,
    bookingDetails: {},
    emailSent: false
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeTab.messages]);

  // Check if conversation is completed
  const isConversationCompleted = activeTab.bookingStatus === 'complete';
  
  // =================== CAREER EXPLORER FUNCTIONS ===================
  
  const validateCareerForm = () => {
    const errors = { mbti: '', holland: '' };
    let isValid = true;
    
    // MBTI validation
    if (!mbtiResult.trim()) {
      errors.mbti = 'MBTI result is required';
      isValid = false;
    } else if (!/^[EI][SN][TF][JP]$/i.test(mbtiResult.trim())) {
      errors.mbti = 'Please enter a valid MBTI type (e.g., ESFP, INTJ)';
      isValid = false;
    }
    
    // Holland validation
    const hollandValues = Object.values(hollandResults);
    const hasAnyHollandValue = hollandValues.some(value => value.trim() !== '');
    
    if (!hasAnyHollandValue) {
      errors.holland = 'At least one Holland score is required';
      isValid = false;
    } else {
      const invalidScores = hollandValues.filter(value => {
        if (value.trim() === '') return false;
        const score = parseInt(value);
        return isNaN(score) || score < 0 || score > 100;
      });
      
      if (invalidScores.length > 0) {
        errors.holland = 'Holland scores must be numbers between 0-100';
        isValid = false;
      }
    }
    
    setCareerFormErrors(errors);
    return isValid;
  };
  
  const analyzeCareerResults = () => {
    const mbti = mbtiResult.trim().toUpperCase();
    const holland = hollandResults;
    
    // MBTI personality descriptions
    const mbtiDescriptions: Record<string, { traits: string[], strengths: string[], weaknesses: string[] }> = {
      'ESFP': {
        traits: ['Enthusiastic', 'Creative', 'Spontaneous', 'People-oriented'],
        strengths: ['Great communication skills', 'Adaptable', 'Optimistic', 'Team player'],
        weaknesses: ['May struggle with long-term planning', 'Can be easily distracted', 'Avoids conflict']
      },
      'INTJ': {
        traits: ['Strategic', 'Independent', 'Analytical', 'Goal-oriented'],
        strengths: ['Excellent problem-solving', 'Strategic thinking', 'Self-motivated', 'Innovative'],
        weaknesses: ['Can be overly critical', 'May neglect emotions', 'Impatient with inefficiency']
      },
      'ENFP': {
        traits: ['Imaginative', 'Energetic', 'Empathetic', 'Flexible'],
        strengths: ['Creative thinking', 'Motivational', 'Open-minded', 'Good with people'],
        weaknesses: ['Can be disorganized', 'May lose interest quickly', 'Overthinks decisions']
      },
      'ISTJ': {
        traits: ['Responsible', 'Organized', 'Detail-oriented', 'Traditional'],
        strengths: ['Reliable', 'Systematic approach', 'Good follow-through', 'Practical'],
        weaknesses: ['May resist change', 'Can be inflexible', 'May overlook big picture']
      }
      // Add more MBTI types as needed
    };
    
    // Calculate top Holland codes
    const hollandScores = Object.entries(holland)
      .filter(([_, score]) => score.trim() !== '')
      .map(([type, score]) => ({ type, score: parseInt(score) || 0 }))
      .sort((a, b) => b.score - a.score);
    
    const topHollandCodes = hollandScores.slice(0, 3).map(item => item.type.charAt(0).toUpperCase()).join('');
    
    // Career suggestions based on MBTI and Holland combination
    const careerSuggestions = generateCareerSuggestions(mbti, topHollandCodes);
    
    return {
      mbtiType: mbti,
      hollandCode: topHollandCodes,
      careerSuggestions: careerSuggestions,
      personalityTraits: mbtiDescriptions[mbti]?.traits || ['Unique', 'Individual', 'Special'],
      strengths: mbtiDescriptions[mbti]?.strengths || ['Strong analytical skills', 'Good communication'],
      growthAreas: mbtiDescriptions[mbti]?.weaknesses || ['Areas for development', 'Growth opportunities']
    };
  };
  
  const generateCareerSuggestions = (mbti: string, hollandCode: string) => {
    // Career database based on MBTI and Holland combinations
    const careerDatabase: Record<string, Array<{
      title: string;
      description: string;
      matchPercentage: number;
      requiredSkills: string[];
      universities: string[];
    }>> = {
      'ESFP-RIA': [
        {
          title: 'Physical Therapist',
          description: 'Help patients recover from injuries through hands-on treatment and exercise programs.',
          matchPercentage: 92,
          requiredSkills: ['Interpersonal skills', 'Physical fitness', 'Problem-solving', 'Patience'],
          universities: ['University of Medicine and Pharmacy HCMC', 'Hanoi Medical University']
        },
        {
          title: 'Occupational Therapist',
          description: 'Assist people with disabilities or injuries to develop, recover, or maintain daily living skills.',
          matchPercentage: 88,
          requiredSkills: ['Creativity', 'Communication', 'Analytical thinking', 'Compassion'],
          universities: ['University of Medicine and Pharmacy HCMC', 'Hue University of Medicine']
        }
      ],
      'INTJ-IAS': [
        {
          title: 'Research Scientist',
          description: 'Conduct research to develop new knowledge, products, or technologies.',
          matchPercentage: 95,
          requiredSkills: ['Critical thinking', 'Research methods', 'Data analysis', 'Technical writing'],
          universities: ['Vietnam National University', 'Ho Chi Minh City University of Technology']
        },
        {
          title: 'Software Architect',
          description: 'Design and oversee the development of complex software systems.',
          matchPercentage: 90,
          requiredSkills: ['Programming', 'System design', 'Leadership', 'Problem-solving'],
          universities: ['FPT University', 'University of Information Technology VNU-HCM']
        }
      ],
      'ENFP-SAE': [
        {
          title: 'Marketing Manager',
          description: 'Develop and implement marketing strategies to promote products or services.',
          matchPercentage: 89,
          requiredSkills: ['Creativity', 'Communication', 'Strategic thinking', 'Market analysis'],
          universities: ['Foreign Trade University', 'University of Economics HCMC']
        },
        {
          title: 'Human Resources Manager',
          description: 'Oversee employee relations, recruitment, and organizational development.',
          matchPercentage: 85,
          requiredSkills: ['Leadership', 'Communication', 'Problem-solving', 'Organizational skills'],
          universities: ['University of Labor and Social Affairs', 'Banking University HCMC']
        }
      ]
    };
    
    // Default career suggestions if specific combination not found
    const defaultCareers = [
      {
        title: 'Business Analyst',
        description: 'Analyze business processes and recommend improvements.',
        matchPercentage: 75,
        requiredSkills: ['Analytical thinking', 'Communication', 'Problem-solving'],
        universities: ['University of Economics HCMC', 'Foreign Trade University']
      },
      {
        title: 'Project Manager',
        description: 'Plan, execute, and oversee projects from start to finish.',
        matchPercentage: 70,
        requiredSkills: ['Leadership', 'Organization', 'Communication', 'Time management'],
        universities: ['RMIT University Vietnam', 'University of Economics HCMC']
      }
    ];
    
    const key = `${mbti}-${hollandCode}`;
    return careerDatabase[key] || defaultCareers;
  };
  
  const handleCareerFormSubmit = async () => {
    if (!validateCareerForm()) {
      return;
    }
    
    setCareerAnalysis(prev => ({ ...prev, isAnalyzing: true, error: null }));
    
    try {
      // Prepare API request data
      const requestData = {
        mbti_type: mbtiResult.trim().toUpperCase(),
        holland_scores: {
          realistic: parseInt(hollandResults.realistic) || 0,
          investigative: parseInt(hollandResults.investigative) || 0,
          artistic: parseInt(hollandResults.artistic) || 0,
          social: parseInt(hollandResults.social) || 0,
          enterprising: parseInt(hollandResults.enterprising) || 0,
          conventional: parseInt(hollandResults.conventional) || 0,
        }
      };
      
      // Call API to analyze career path
      const analysisResults = await careerAnalysisApi.createAnalysis(requestData);
      
      setCareerAnalysis({
        isAnalyzing: false,
        results: analysisResults,
        error: null
      });
      
    } catch (error: any) {
      console.error('Career analysis failed:', error);
      setCareerAnalysis({
        isAnalyzing: false,
        results: null,
        error: error.response?.data?.detail || 'Failed to analyze career results. Please try again.'
      });
    }
  };

  // =================== CAREER HELPER FUNCTIONS ===================
  
  const checkIfCareerRelated = async (message: string): Promise<boolean> => {
    const lowerMessage = message.toLowerCase();
    
    // Career-related keywords
    const careerKeywords = [
      'career', 'job', 'work', 'profession', 'employment', 'occupation',
      'salary', 'resume', 'cv', 'interview', 'skills', 'qualification',
      'university', 'college', 'degree', 'major', 'study', 'education',
      'internship', 'training', 'certification', 'course',
      'mbti', 'holland', 'personality', 'interest', 'strength', 'weakness',
      'future', 'goal', 'plan', 'advice', 'guidance', 'counseling',
      'industry', 'field', 'sector', 'company', 'organization',
      'nghề nghiệp', 'công việc', 'làm việc', 'lương', 'phỏng vấn',
      'kỹ năng', 'đại học', 'học tập', 'giáo dục', 'thực tập',
      'tương lai', 'mục tiêu', 'kế hoạch', 'tư vấn', 'hướng dẫn'
    ];
    
    // Check if message contains career-related keywords
    return careerKeywords.some(keyword => lowerMessage.includes(keyword));
  };

  // =================== BOOKING HANDLERS ===================
  const handleBookingOptionSelect = (option: BookingOption) => {
    // Check if conversation is completed
    if (activeTab.bookingStatus === 'complete') {
      return;
    }
    
    // Create confirmation message from bot
    const confirmationText = `Do you want to confirm booking with ${option.lecturer_name} on ${option.date} at ${option.time} for ${option.subject}?\n\n📍 ${option.location}\n⏱️ ${option.duration_minutes} minutes`;
    
    const confirmationMessage: MessageType = {
      id: Date.now().toString(),
      content: confirmationText,
      sender: 'bot',
      timestamp: new Date(),
      awaitingConfirmation: {
        option,
        confirmationText
      }
    };
    
    onAddMessage(activeTab.id, confirmationMessage);
  };

  const handleConfirmBooking = async (option: BookingOption) => {
    // Check if conversation is completed
    if (activeTab.bookingStatus === 'complete') {
      return;
    }
    
    if (!activeTab.conversationId) {
      
      const conversationTabs = tabs?.filter((tab: ChatTab) => tab.type === 'conversation' && tab.conversationId) || [];
      const latestConversationTab = conversationTabs[conversationTabs.length - 1];
      
      if (latestConversationTab?.conversationId) {
        const fallbackConversationId = latestConversationTab.conversationId;
        
        await performBookingConfirmation(option, fallbackConversationId);
        return;
      }
      
      const errorMessage: MessageType = {
        id: Date.now().toString(),
        content: "Sorry, there was an error confirming your booking. Please try starting a new conversation.",
        sender: 'bot',
        timestamp: new Date(),
      };
      onAddMessage(activeTab.id, errorMessage);
      return;
    }
    
    await performBookingConfirmation(option, activeTab.conversationId);
  };

  const performBookingConfirmation = async (option: BookingOption, conversationId: number) => {
    
    
    setConfirmationProcessing('confirming');
    
    // Add user's "Yes" response immediately
    const userYesMessage: MessageType = {
      id: Date.now().toString(),
      content: "Yes",
      sender: 'user',
      timestamp: new Date(),
    };
    onAddMessage(activeTab.id, userYesMessage);

    try {
      const bookingData = {
        conversation_id: conversationId,
        availability_id: option.availability_id,
        lecturer_name: option.lecturer_name,
        date: option.date,
        time: option.time,
        subject: option.subject,
        location: option.location,
        duration_minutes: option.duration_minutes
      };
      
      const response = await chatbotApi.confirmBooking(bookingData);
      
      // Add success response from API
      const successMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };
      onAddMessage(activeTab.id, successMessage);
      
      // Update tab booking status immediately
      if (response.booking_status && updateTabBookingStatus) {
        console.log('🎯 Updating booking status to:', response.booking_status);
        updateTabBookingStatus(activeTab.id, response.booking_status);
      }
      
      // Show modal if booking was successful and email info is available
      if (response.email_sent !== undefined) {
        setBookingSuccessModal({
          isOpen: true,
          bookingDetails: {
            lecturer_name: option.lecturer_name,
            date: option.date,
            time: option.time,
            subject: option.subject,
            location: option.location,
            duration_minutes: option.duration_minutes
          },
          emailSent: response.email_sent
        });
      }
      
    } catch (error) {
      console.error('Booking confirmation failed:', error);
      const errorMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: "Sorry, there was an error confirming your booking. Please try again.",
        sender: 'bot',
        timestamp: new Date(),
      };
      onAddMessage(activeTab.id, errorMessage);
    } finally {
      // Clear confirmation processing state
      setTimeout(() => {
        setConfirmationProcessing(null);
      }, 1000);
    }
  };

  const handleCancelBooking = async () => {
    // Check if conversation is completed
    if (activeTab.bookingStatus === 'complete') {
      return;
    }
    
    if (!activeTab.conversationId) {
      const errorMessage: MessageType = {
        id: Date.now().toString(),
        content: "Sorry, there was an error. Please try starting a new conversation.",
        sender: 'bot',
        timestamp: new Date(),
      };
      onAddMessage(activeTab.id, errorMessage);
      return;
    }
    
    setConfirmationProcessing('cancelling');
    
    try {
      // Call booking cancellation API
      const response = await chatbotApi.cancelBooking(activeTab.conversationId);
      
      // Add user's "No" response
      const userNoMessage: MessageType = {
        id: Date.now().toString(),
        content: "No",
        sender: 'user',
        timestamp: new Date(),
      };
      
      // Add bot's continue response from API
      const continueMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: 'bot',
        timestamp: new Date(),
      };
      
      onAddMessage(activeTab.id, userNoMessage);
      onAddMessage(activeTab.id, continueMessage);
      
    } catch (error) {
      console.error('Booking cancellation failed:', error);
      // Fallback to local messages
      const userNoMessage: MessageType = {
        id: Date.now().toString(),
        content: "No",
        sender: 'user',
        timestamp: new Date(),
      };
      
      const continueMessage: MessageType = {
        id: (Date.now() + 1).toString(),
        content: "No problem! I can help you find another time or answer any more questions about booking. Do you need any more help?",
        sender: 'bot',
        timestamp: new Date(),
      };
      
      onAddMessage(activeTab.id, userNoMessage);
      onAddMessage(activeTab.id, continueMessage);
    } finally {
      // Clear confirmation processing state
      setTimeout(() => {
        setConfirmationProcessing(null);
      }, 500);
    }
  };

  const handleSendMessage = async () => {
    // Check if chat is blocked
    if (isBlocked) {
      return;
    }
    
    const validation = validateMessage(message);
    if (!validation.isValid) {
      setValidationError(validation.error || '');
      return;
    }

    setIsLoading(true);
    setValidationError('');
    setValidationWarning('');
    setModerationWarning('');

    // Add user message immediately
    const userMessage: MessageType = {
      id: Date.now().toString(),
      content: message,
      sender: 'user',
      timestamp: new Date(),
    };

    // If this is new-chat tab, create a new conversation tab first
    let targetTabId = activeTab.id;
    let conversationId = activeTab.conversationId;

    if (activeTab.type === 'new-chat') {
      targetTabId = onCreateNewTab();
    }

    onAddMessage(targetTabId, userMessage);
    setMessage('');

    try {
      // Check if this is a career-related question and user has career analysis
      const isCareerQuestion = await checkIfCareerRelated(message);
      
      if (isCareerQuestion) {
        try {
          // Try to get user's latest career analysis
          const latestAnalysis = await careerAnalysisApi.getLatestAnalysis();
          
          // Use career chat API for contextual response
          const careerResponse = await careerAnalysisApi.chatAboutCareer({
            analysis_id: latestAnalysis.id,
            user_question: message,
          });
          
          // Add career counselor response
          const careerMessage: MessageType = {
            id: (Date.now() + 1).toString(),
            content: careerResponse.response,
            sender: 'bot',
            timestamp: new Date(),
            isAppropriate: true
          };
          
          onAddMessage(targetTabId, careerMessage);
          setIsLoading(false);
          return;
          
        } catch (careerError) {
          // If no career analysis found, suggest taking the test
          const suggestionMessage: MessageType = {
            id: (Date.now() + 1).toString(),
            content: "I'd love to help you with career guidance! To give you personalized advice, please take the Career Explorer assessment first. Click on the 'Career Explorer' tab to get started with your MBTI and Holland tests.",
            sender: 'bot',
            timestamp: new Date(),
            isAppropriate: true
          };
          
          onAddMessage(targetTabId, suggestionMessage);
          setIsLoading(false);
          return;
        }
      }

      // Regular chatbot flow for non-career questions
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
            // Silent fail for refresh
          }
        }
        
        // Determine bot message content
        let botContent = response.response;
        
        // If there are booking options, show simplified message
        if (response.booking_options && response.booking_options.length > 0) {
          botContent = `I found ${response.booking_options.length} time slots that match your request. Please select the time slot you want to book:`;
        }
        
        // Add bot response to the target tab WITH BOOKING OPTIONS
        const botMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          content: botContent,
          sender: 'bot',
          timestamp: new Date(),
          isAppropriate: response.is_appropriate,
          bookingOptions: response.booking_options || [],
          warningMessage: response.warning_message
        };

        onAddMessage(targetTabId, botMessage);
      }

      if (response.conversation_id && response.conversation_id > 0) {
        if (activeTab.type === 'new-chat' && onUpdateTabConversationId) {
          onUpdateTabConversationId(targetTabId, response.conversation_id);
        }
        
        if (onConversationChange) {
          onConversationChange(response.conversation_id);
        }
      }

    } catch (error) {
      // Handle account suspension
      if (error instanceof Error && error.message.includes('suspended')) {
        setIsBlocked(true);
        setModerationWarning('Your account has been suspended due to policy violations. Please contact support.');
        
        try {
          await onRefreshUserData();
        } catch (refreshError) {
          // Silent fail for refresh
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
          <div className="flex flex-col space-y-3 md:space-y-4">
            {/* Bot's initial question */}
            <div className="flex items-start w-full">
              <div className="w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 rounded-full bg-[#332288] flex items-center justify-center flex-shrink-0">
                <Bot className="w-3 h-3 md:w-4 md:h-4 lg:w-6 lg:h-6 text-white" />
              </div>
              <div className="flex-1 flex justify-start pl-2 md:pl-4">
                <div className="w-[90%] md:w-[85%] lg:w-[80%] rounded-lg p-2 md:p-3 lg:p-4 border-2 border-[#332288] bg-white">
                  <p className="text-xs md:text-sm text-[#332288]">
                    Please enter your MBTI and Holland test results to get personalized career recommendations!
                  </p>
                </div>
              </div>
            </div>

            {/* Test Results Form */}
            {!careerAnalysis.results && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="flex items-start w-full"
              >
                <div className="w-6 h-6 md:w-8 md:h-8 lg:w-10 lg:h-10 rounded-full bg-[#332288] flex items-center justify-center flex-shrink-0">
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
                        placeholder="Enter your MBTI result (e.g., ESFP, INTJ)"
                        className={`w-full md:w-[70%] lg:w-[50%] px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-xs md:text-sm lg:text-base ${
                          careerFormErrors.mbti ? 'border-red-500' : 'border-[#332288]'
                        }`}
                        disabled={careerAnalysis.isAnalyzing}
                      />
                      {careerFormErrors.mbti && (
                        <p className="text-red-500 text-xs mt-1">{careerFormErrors.mbti}</p>
                      )}
                    </motion.div>

                    {/* Holland Test */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="mb-4 md:mb-6"
                    >
                      <h3 className="text-sm md:text-base font-semibold text-[#332288] mb-3 md:mb-4">Holland Test* (Enter scores 0-100)</h3>
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
                              type="number"
                              min="0"
                              max="100"
                              value={value}
                              onChange={(e) => setHollandResults(prev => ({
                                ...prev,
                                [type]: e.target.value
                              }))}
                              placeholder="0-100"
                              className={`w-full md:w-[120px] lg:w-[150px] px-2 md:px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-[#332288] bg-white text-black text-xs md:text-sm lg:text-base ${
                                careerFormErrors.holland ? 'border-red-500' : 'border-[#332288]'
                              }`}
                              disabled={careerAnalysis.isAnalyzing}
                            />
                          </motion.div>
                        ))}
                      </div>
                      {careerFormErrors.holland && (
                        <p className="text-red-500 text-xs mt-2">{careerFormErrors.holland}</p>
                      )}
                    </motion.div>

                    {/* Submit Button */}
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                      className="flex justify-center"
                    >
                      <button
                        onClick={handleCareerFormSubmit}
                        disabled={careerAnalysis.isAnalyzing}
                        className={`px-6 py-3 rounded-lg font-semibold text-white transition-all duration-200 ${
                          careerAnalysis.isAnalyzing
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-[#332288] hover:bg-[#443399] active:scale-95'
                        }`}
                      >
                        {careerAnalysis.isAnalyzing ? (
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            <span>Analyzing...</span>
                          </div>
                        ) : (
                          'Analyze My Career Path'
                        )}
                      </button>
                    </motion.div>

                    {/* Error Display */}
                    {careerAnalysis.error && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-center"
                      >
                        <p className="text-red-700 text-sm">{careerAnalysis.error}</p>
                      </motion.div>
                    )}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Career Analysis Results */}
            {careerAnalysis.results && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-4"
              >
                {/* Bot Analysis Response */}
                <div className="flex items-start w-full">
                  <div className="w-6 h-6 md:w-8 md:h-8 rounded-full bg-[#332288] flex items-center justify-center flex-shrink-0">
                    <Bot className="w-3 h-3 md:w-4 md:h-4 text-white" />
                  </div>
                  <div className="flex-1 flex justify-start pl-2 md:pl-4">
                    <div className="w-[90%] md:w-[85%] lg:w-[80%] rounded-lg p-4 border-2 border-[#332288] bg-white space-y-4">
                      
                      {/* Personality Overview */}
                      <div>
                        <h3 className="text-lg font-bold text-[#332288] mb-2">Your Personality Profile</h3>
                        <p className="text-sm mb-2 text-gray-600">
                          <strong>MBTI Type:</strong> {careerAnalysis.results.mbti_type}
                        </p>
                        <p className="text-sm mb-2 text-gray-600">
                          <strong>Holland Code:</strong> {careerAnalysis.results.holland_code}
                        </p>
                        <div className="flex flex-wrap gap-1 mb-3">
                          {careerAnalysis.results.personality_traits?.map((trait: string, index: number) => (
                            <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              {trait}
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Strengths & Weaknesses */}
                      <div className="grid md:grid-cols-2 gap-4">
                        <div className="bg-green-50 p-3 rounded-lg">
                          <h4 className="font-semibold text-green-800 mb-2">💪 Strengths</h4>
                          <ul className="text-sm text-green-700 space-y-1">
                            {careerAnalysis.results.strengths?.map((strength: string, index: number) => (
                              <li key={index}>• {strength}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="bg-orange-50 p-3 rounded-lg">
                          <h4 className="font-semibold text-orange-800 mb-2">🎯 Growth Areas</h4>
                          <ul className="text-sm text-orange-700 space-y-1">
                            {careerAnalysis.results.growth_areas?.map((weakness: string, index: number) => (
                              <li key={index}>• {weakness}</li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      {/* Career Suggestions */}
                      <div>
                        <h3 className="text-lg font-bold text-[#332288] mb-3">🎓 Recommended Career Paths</h3>
                        <div className="space-y-3">
                          {careerAnalysis.results.career_suggestions?.map((career: any, index: number) => (
                            <div key={index} className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors">
                              <div className="flex justify-between items-start mb-2">
                                <h4 className="font-semibold text-[#332288]">{career.title}</h4>
                                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded font-medium">
                                  {career.match_percentage}% match
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-2">{career.description}</p>
                              
                              <div className="text-xs">
                                <p className="mb-1 text-gray-600"><strong>Required Skills:</strong> {career.required_skills.join(', ')}</p>
                                <p className="text-gray-600"><strong>Universities:</strong> {career.universities.join(', ')}</p>
                                {career.industry && <p className="text-gray-600"><strong>Industry:</strong> {career.industry}</p>}
                                {career.salary_range && <p className="text-gray-600"><strong>Salary Range:</strong> {career.salary_range}</p>}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Detailed Analysis */}
                      {careerAnalysis.results.detailed_analysis && (
                        <div className="bg-blue-50 p-4 rounded-lg">
                          <h4 className="font-semibold text-blue-800 mb-2">📝 Detailed Analysis</h4>
                          <p className="text-sm text-blue-700 whitespace-pre-wrap">{careerAnalysis.results.detailed_analysis}</p>
                        </div>
                      )}

                      {/* Recommendations */}
                      {careerAnalysis.results.recommendations && (
                        <div className="bg-purple-50 p-4 rounded-lg">
                          <h4 className="font-semibold text-purple-800 mb-2">💡 Recommendations</h4>
                          <p className="text-sm text-purple-700 whitespace-pre-wrap">{careerAnalysis.results.recommendations}</p>
                        </div>
                      )}

                      {/* Reset Button */}
                      <div className="text-center pt-4 border-t border-gray-200">
                        <button
                          onClick={() => {
                            setCareerAnalysis({ isAnalyzing: false, results: null, error: null });
                            setMbtiResult('');
                            setHollandResults({
                              realistic: '',
                              investigative: '',
                              artistic: '',
                              social: '',
                              enterprising: '',
                              conventional: ''
                            });
                            setCareerFormErrors({ mbti: '', holland: '' });
                          }}
                          className="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg text-sm transition-colors"
                        >
                          Take Another Test
                        </button>
                      </div>
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

  // Chat Tab (new-chat or conversation) - WITH BOOKING SUPPORT
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
                      : "Please complete your schedule to start the conversation."
                    }
                  </p>
                </>
              ) : (
                <>
                  <p className="text-sm md:text-base">Start the conversation by typing your message below.</p>
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
              
              <div className="flex flex-col max-w-[85%] md:max-w-[80%]">
                <div
                  className={`rounded-lg p-2 md:p-3 ${
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

                {/* =================== BOOKING OPTIONS =================== */}
                {msg.bookingOptions && msg.bookingOptions.length > 0 && !isConversationCompleted && (
                  <div className="mt-2">
                    <BookingOptions 
                      options={msg.bookingOptions} 
                      onOptionSelect={handleBookingOptionSelect}
                      disabled={isConversationCompleted}
                    />
                  </div>
                )}

                {/* Completion notice for booking options */}
                {msg.bookingOptions && msg.bookingOptions.length > 0 && isConversationCompleted && (
                  <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-sm text-green-700">✅ This conversation has been completed. Your booking has been confirmed.</p>
                  </div>
                )}

                {/* =================== WARNING MESSAGE =================== */}
                {msg.warningMessage && (
                  <div className="mt-2 p-2 bg-yellow-100 border border-yellow-400 rounded-lg">
                    <p className="text-xs text-yellow-800">{msg.warningMessage}</p>
                  </div>
                )}

                {/* =================== CONFIRMATION BUTTONS =================== */}
                {msg.awaitingConfirmation && !isConversationCompleted && (
                  <div className="mt-4 flex justify-center">
                    <ConfirmationButtons
                      onConfirm={() => handleConfirmBooking(msg.awaitingConfirmation!.option)}
                      onCancel={handleCancelBooking}
                      confirmText="Yes"
                      cancelText="No"
                      disabled={!!confirmationProcessing || isConversationCompleted}
                    />
                  </div>
                )}

                {/* Completion notice for confirmation buttons */}
                {msg.awaitingConfirmation && isConversationCompleted && (
                  <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg text-center">
                    <p className="text-sm text-green-700">✅ Booking confirmed - conversation completed</p>
                  </div>
                )}
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
          
          {/* Scroll anchor */}
          <div ref={messagesEndRef} />
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

        {/* Conversation completed notice */}
        {isConversationCompleted && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
              <p className="text-sm text-green-700 font-medium">Conversation Completed</p>
            </div>
            <p className="text-xs text-green-600 mt-1">
              Your booking has been confirmed. Start a new conversation to make another appointment.
            </p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="flex gap-2 md:gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={handleInputChange}
              placeholder={
                isConversationCompleted ? "Conversation completed - start new chat for another booking" :
                isInputDisabled || isBlocked ? "Current chat is disabled" : 
                "Type your message here..."
              }
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
              disabled={isInputDisabled || isLoading || isBlocked || isConversationCompleted}
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
            disabled={!message.trim() || isLoading || isInputDisabled || !!validationError || isBlocked || isConversationCompleted}
                          className={`px-3 md:px-4 py-2 rounded-lg font-medium transition-all duration-200 text-sm md:text-base ${
                !message.trim() || isLoading || isInputDisabled || !!validationError || isBlocked || isConversationCompleted
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

      {/* Booking Success Modal */}
      <BookingSuccessModal
        isOpen={bookingSuccessModal.isOpen}
        onClose={() => setBookingSuccessModal(prev => ({ ...prev, isOpen: false }))}
        bookingDetails={bookingSuccessModal.bookingDetails}
        emailSent={bookingSuccessModal.emailSent}
      />
    </div>
  );
};

export default ChatWindowTabs; 