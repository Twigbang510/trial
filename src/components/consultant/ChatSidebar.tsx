import { MessageSquare, Compass } from 'lucide-react';

interface ChatSidebarProps {
  activeTab: 'new-chat' | 'career-explorer';
  onTabChange: (tab: 'new-chat' | 'career-explorer') => void;
}

export const ChatSidebar = ({ activeTab, onTabChange }: ChatSidebarProps) => {
  return (
    <div className="w-80 bg-white flex flex-col h-full">

      {/* Tabs */}
      <div className="flex-1 p-4 space-y-4">
        <button
          onClick={() => onTabChange('new-chat')}
          className={`w-full h-16 flex items-center gap-3 px-4 rounded-lg transition-colors ${
            activeTab === 'new-chat'
              ? 'bg-[#332288] text-white'
              : 'border border-[#332288] text-[#332288] hover:bg-gray-50'
          }`}
        >
          <MessageSquare className="w-5 h-5" />
          <span>Begin a New Chat</span>
        </button>

        <button
          onClick={() => onTabChange('career-explorer')}
          className={`w-full h-16 flex items-center gap-3 px-4 rounded-lg transition-colors ${
            activeTab === 'career-explorer'
              ? 'bg-[#332288] text-white'
              : 'border border-[#332288] text-[#332288] hover:bg-gray-50'
          }`}
        >
          <Compass className="w-5 h-5" />
          <span>Career Explorer</span>
        </button>
      </div>
    </div>
  );
}; 