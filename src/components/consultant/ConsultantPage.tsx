import { useState } from 'react';
import { ChatSidebar } from './ChatSidebar';
import ChatWindow from './ChatWindow';
import { Navbar } from '../landing/Navbar';

export const ConsultantPage = () => {
  const [activeTab, setActiveTab] = useState<'new-chat' | 'career-explorer'>('new-chat');
  // const [currentConversationId, setCurrentConversationId] = useState<number | undefined>();

      const handleConversationChange = (conversationId: number) => {
      // setCurrentConversationId(conversationId);
      console.log('Conversation changed:', conversationId);
    };

  return (
    <div className="min-h-screen w-screen bg-white text-text-primary overflow-auto">
      <Navbar />
      <div className="mt-[148px] h-[calc(100vh-148px)] flex flex-col md:flex-row px-2 md:px-4">
        {/* Left Sidebar */}
        <ChatSidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
        {/* Main Chat Area */}
        <ChatWindow 
          activeTab={activeTab} 
          onConversationChange={handleConversationChange}
        />
      </div>
    </div>
  );
}; 