import React, { useState } from 'react';
import { ChatSidebar } from './ChatSidebar';
import ChatWindowTabs from './ChatWindowTabs';
import { Navbar } from '../landing/Navbar';
import { useAuth } from '@/hooks/useAuth';
import { useChatTabs } from '@/hooks/useChatTabs';

export const ConsultantPage = () => {
  const { user, refreshUserData } = useAuth();
  const {
    tabs,
    activeTabId,
    setActiveTab,
    addMessageToTab,
    createNewChatTab,
    closeTab,
    updateTabConversationId
  } = useChatTabs();

  const activeTab = tabs.find(tab => tab.id === activeTabId) || tabs[0];
  const canCreateNewChat = user?.status === "Not Schedule";

  const handleConversationChange = (conversationId: number) => {
    // Load conversation messages or handle conversation updates
    console.log('Conversation changed:', conversationId);
  };

  return (
    <div className="min-h-screen w-screen bg-white text-text-primary overflow-hidden">
      <Navbar />
      
      <div className="mt-[148px] h-[calc(100vh-148px)] flex flex-col md:flex-row">
        {/* Sidebar */}
        <div className="flex-shrink-0">
          <ChatSidebar
            tabs={tabs}
            activeTabId={activeTabId} 
            onTabChange={setActiveTab}
            onCloseTab={closeTab}
            canCreateNewChat={canCreateNewChat}
            onCreateNewChat={createNewChatTab}
          />
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 p-2 md:p-4 min-w-0 overflow-hidden">
          <ChatWindowTabs
            activeTab={activeTab}
            onAddMessage={addMessageToTab}
            onConversationChange={handleConversationChange}
            onUpdateTabConversationId={updateTabConversationId}
            canCreateNewChat={canCreateNewChat}
            onCreateNewTab={createNewChatTab}
            onRefreshUserData={refreshUserData}
          />
        </div>
      </div>
    </div>
  );
}; 