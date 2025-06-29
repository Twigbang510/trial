import { MessageSquare, Compass, X, Plus, ChevronDown, ChevronRight, Menu } from 'lucide-react';
import { ChatTab } from '@/types/conversation.type';
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ChatSidebarProps {
  tabs: ChatTab[];
  activeTabId: string | null;
  onTabChange: (tabId: string) => void;
  onCloseTab: (tabId: string) => void;
  canCreateNewChat: boolean;
  onCreateNewChat: () => void;
}

export const ChatSidebar = ({ 
  tabs, 
  activeTabId, 
  onTabChange, 
  onCloseTab,
  canCreateNewChat,
  onCreateNewChat
}: ChatSidebarProps) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const getTabIcon = (type: string) => {
    switch (type) {
      case 'career-explorer':
        return <Compass className="w-4 h-4" />;
      case 'new-chat':
        return <Plus className="w-4 h-4" />;
      default:
        return <MessageSquare className="w-4 h-4" />;
    }
  };

  const handleTabClick = (tabId: string, type: string) => {
    onTabChange(tabId);
    // Close mobile menu when tab is selected
    setIsMobileMenuOpen(false);
  };

  // Separate default tabs and conversation tabs
  const defaultTabs = tabs.filter(tab => tab.type !== 'conversation');
  const conversationTabs = tabs.filter(tab => tab.type === 'conversation');

  const SidebarContent = () => (
    <>
      {/* Header */}
      <div className="p-3 md:p-4 border-b border-gray-100">
        <h2 className="text-base md:text-lg font-semibold text-gray-800">Chat Sessions</h2>
        <p className="text-xs md:text-sm text-gray-500 mt-1">Select or create a new conversation</p>
      </div>

      {/* Tabs */}
      <div className="flex-1 p-2 md:p-3 space-y-1 overflow-y-auto">
        {/* Default Tabs */}
        {defaultTabs.map((tab) => {
          const isDisabled = tab.type === 'new-chat' && !canCreateNewChat;
          const isNewChatTab = tab.type === 'new-chat';
          const hasConversations = conversationTabs.length > 0;
          
          return (
            <div key={tab.id} className="space-y-1">
              {/* Main Tab */}
              <div
                className={`relative group cursor-pointer rounded-lg transition-colors duration-200 ${
                  tab.isActive
                    ? 'bg-[#332288] text-white shadow-sm'
                    : isDisabled
                    ? 'bg-gray-50 text-gray-400 cursor-not-allowed'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-[#332288]'
                }`}
                onClick={() => !isDisabled && handleTabClick(tab.id, tab.type)}
              >
                <div className="flex items-center px-2 md:px-3 py-2 md:py-3 gap-2 md:gap-3">
                  <div className={`flex-shrink-0 ${
                    tab.isActive 
                      ? 'text-white' 
                      : isDisabled 
                      ? 'text-gray-400' 
                      : 'text-gray-500'
                  }`}>
                    {getTabIcon(tab.type)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className={`text-sm font-medium truncate ${
                      isDisabled ? 'text-gray-400' : ''
                    }`}>
                      {tab.title}
                    </p>
                    <p className={`text-xs mt-1 hidden md:block ${
                      tab.isActive 
                        ? 'text-white/80' 
                        : isDisabled 
                        ? 'text-gray-400' 
                        : 'text-gray-500'
                    }`}>
                      {tab.type === 'new-chat' && 'Start a new conversation'}
                      {tab.type === 'career-explorer' && 'Explore career guidance'}
                    </p>
                  </div>
                </div>

                {/* Active indicator */}
                {tab.isActive && (
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"></div>
                )}
              </div>

              {/* Conversation Tabs Tree (only show under new-chat) */}
              {isNewChatTab && conversationTabs.map((convTab) => (
                <div
                  key={convTab.id}
                  className={`relative group cursor-pointer rounded-lg transition-colors duration-200 ml-4 md:ml-6 ${
                    convTab.isActive
                      ? 'bg-[#332288] text-white shadow-sm'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-[#332288]'
                  }`}
                  onClick={() => handleTabClick(convTab.id, convTab.type)}
                >
                  {/* Tree connection line */}
                  <div className="absolute -left-2 md:-left-3 top-0 bottom-0 w-px bg-gray-200"></div>
                  <div className="absolute -left-2 md:-left-3 top-3 md:top-4 w-2 md:w-3 h-px bg-gray-200"></div>
                  
                  <div className="flex items-center px-2 md:px-3 py-1.5 md:py-2 gap-2 md:gap-3">
                    <div className={`flex-shrink-0 ${
                      convTab.isActive ? 'text-white' : 'text-gray-500'
                    }`}>
                      <MessageSquare className="w-3 h-3" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate`}>
                        {convTab.title}
                      </p>
                      {convTab.messages.length > 0 && (
                        <p className={`text-xs truncate mt-1 hidden md:block ${
                          convTab.isActive ? 'text-white/80' : 'text-gray-500'
                        }`}>
                          {convTab.messages[convTab.messages.length - 1]?.content}
                        </p>
                      )}
                    </div>

                    {/* Close button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onCloseTab(convTab.id);
                      }}
                      className={`opacity-0 group-hover:opacity-100 p-1 rounded transition-opacity ${
                        convTab.isActive 
                          ? 'hover:bg-white/20 text-white' 
                          : 'hover:bg-gray-200 text-gray-500'
                      }`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>

                  {/* Active indicator */}
                  {convTab.isActive && (
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"></div>
                  )}
                </div>
              ))}
            </div>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileMenuOpen(true)}
        className="md:hidden fixed top-[160px] left-4 z-40 bg-[#332288] text-white p-2 rounded-lg shadow-lg hover:bg-[#2a1f70] transition-colors"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Desktop Sidebar */}
      <div className="hidden md:block w-80 flex-shrink-0 bg-white border-r border-gray-200 h-full">
        <div className="flex flex-col h-full">
          <SidebarContent />
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <div className="md:hidden fixed inset-0 z-50 flex">
            {/* Backdrop */}
            <motion.div 
              className="fixed inset-0 bg-black/50" 
              onClick={() => setIsMobileMenuOpen(false)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            />
            
            {/* Sidebar */}
            <motion.div 
              className="relative w-80 max-w-[85vw] bg-white flex flex-col h-full shadow-xl"
              initial={{ x: "-100%" }}
              animate={{ x: 0 }}
              exit={{ x: "-100%" }}
              transition={{ duration: 0.3, ease: "easeOut" }}
            >
              {/* Close button */}
              <button
                onClick={() => setIsMobileMenuOpen(false)}
                className="absolute top-4 right-4 z-10 p-1 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <X className="w-5 h-5 text-gray-500" />
              </button>
              
              <SidebarContent />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}; 