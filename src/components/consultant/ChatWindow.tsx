import { useState } from 'react';
import { Mic, Paperclip, ArrowRight, User, Bot } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface ChatWindowProps {
  activeTab: 'new-chat' | 'career-explorer';
}

export const ChatWindow = ({ activeTab }: ChatWindowProps) => {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      content: message,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setMessage('');

    // Simulate bot response
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "I'm analyzing your request. Please give me a moment to provide a detailed response.",
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  };

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
        </div>
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-2 md:p-4">   
        <div className="w-full h-16 md:h-20 bg-opacity-30 bg-[#8C8C8C] rounded-full flex items-center gap-1 md:gap-2 p-1 md:p-2">
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
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your prompt here"
            className="flex-1 px-2 md:px-4 py-1 md:py-2 bg-transparent text-[#424242] placeholder-[#424242] focus:outline-none text-sm md:text-base"
          />

          {/* Voice Input Button */}
          <button
            type="button"
            className="p-1 md:p-2 text-[#424242] hover:text-gray-200 transition-colors"
          >
            <Mic className="w-4 h-4 md:w-5 md:h-5" />
          </button>

          {/* Send Button */}
          <button
            type="submit"
            className="p-2 md:p-4 border-2 bg-[#332288] rounded-full text-white hover:text-gray-200 transition-colors"
          >
            <ArrowRight className="w-4 h-4 md:w-5 md:h-5 text-white" />   
          </button>
        </div>
      </form>
    </div>
  );
}; 