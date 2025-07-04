import { useState, useCallback, useEffect } from 'react';
import { ChatTab, ChatTabsState, MessageType } from '@/types/conversation.type';
import chatbotApi from '@/lib/api/chatbot.api';

const DEFAULT_TABS: ChatTab[] = [
  {
    id: 'new-chat',
    title: 'Begin a New Chat',
    messages: [],
    isActive: true,
    type: 'new-chat'
  },
  {
    id: 'career-explorer',
    title: 'Career Explorer',
    messages: [],
    isActive: false,
    type: 'career-explorer'
  }
];

export const useChatTabs = () => {
  const [tabsState, setTabsState] = useState<ChatTabsState>({
    tabs: DEFAULT_TABS,
    activeTabId: 'new-chat'
  });
  const [isLoadingConversations, setIsLoadingConversations] = useState(false);

  // Load existing conversations from backend
  const loadConversations = useCallback(async () => {
    setIsLoadingConversations(true);
    try {
      const conversations = await chatbotApi.getConversations();
      
      if (conversations.length > 0) {
        const conversationTabs: ChatTab[] = conversations.map(conv => ({
          id: `conv-${conv.id}`,
          title: conv.title || `Chat ${conv.id}`,
          conversationId: conv.id,
          messages: [], // Will be loaded when tab is activated
          isActive: false,
          type: 'conversation' as const,
          bookingStatus: conv.booking_status
        }));

        setTabsState(prev => ({
          ...prev,
          tabs: [...DEFAULT_TABS, ...conversationTabs]
        }));
      }
          } catch (error) {
        // Error loading conversations
      } finally {
      setIsLoadingConversations(false);
    }
  }, []);

  // Load messages for a specific conversation
  const loadConversationMessages = useCallback(async (conversationId: number) => {
    try {
      const conversation = await chatbotApi.getConversation(conversationId);
      
      if (conversation && conversation.messages) {
        const messages: MessageType[] = conversation.messages.map((msg) => ({
          id: msg.id.toString(),
          content: msg.content,
          sender: msg.sender as 'user' | 'bot',
          timestamp: new Date(msg.created_at)
        }));

        setTabsState(prev => {
          const updatedTabs = prev.tabs.map(tab => {
            if (tab.conversationId === conversationId) {
              return { 
                ...tab, 
                messages,
                bookingStatus: conversation.booking_status 
              };
            }
            return tab;
          });

          return {
            ...prev,
            tabs: updatedTabs
          };
        });
      }
    } catch (error) {
      // Failed to load conversation messages
    }
  }, []);

  // Load conversations on hook initialization
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const setActiveTab = useCallback((tabId: string) => {    
    setTabsState(prev => {
      const tab = prev.tabs.find(t => t.id === tabId);
      
      if (tab?.type === 'conversation' && tab.conversationId && tab.messages.length === 0) {
        loadConversationMessages(tab.conversationId);
      }

      return {
        ...prev,
        activeTabId: tabId,
        tabs: prev.tabs.map(tab => ({
          ...tab,
          isActive: tab.id === tabId
        }))
      };
    });
  }, [loadConversationMessages]);

  const createNewChatTab = useCallback((conversationId?: number) => {
    const newTabId = conversationId ? `conv-${conversationId}` : `chat-${Date.now()}`;
    const newTab: ChatTab = {
      id: newTabId,
      title: conversationId ? `Chat ${conversationId}` : `Chat ${tabsState.tabs.filter(t => t.type === 'conversation').length + 1}`,
      conversationId,
      messages: [],
      isActive: true,
      type: 'conversation'
    };

    setTabsState(prev => ({
      ...prev,
      activeTabId: newTabId,
      tabs: [
        ...prev.tabs.map(tab => ({ ...tab, isActive: false })),
        newTab
      ]
    }));

    if (conversationId) {
      loadConversationMessages(conversationId);
    }

    return newTabId;
  }, [tabsState.tabs, loadConversationMessages]);

  const closeTab = useCallback((tabId: string) => {
    setTabsState(prev => {
      const tabIndex = prev.tabs.findIndex(tab => tab.id === tabId);
      if (tabIndex === -1 || prev.tabs[tabIndex].type !== 'conversation') {
        return prev; // Can't close default tabs
      }

      const newTabs = prev.tabs.filter(tab => tab.id !== tabId);
      let newActiveTabId = prev.activeTabId;

      // If we're closing the active tab, switch to another tab
      if (prev.activeTabId === tabId) {
        if (tabIndex > 0) {
          newActiveTabId = newTabs[tabIndex - 1].id;
        } else if (newTabs.length > 0) {
          newActiveTabId = newTabs[0].id;
        }
      }

      return {
        tabs: newTabs.map(tab => ({
          ...tab,
          isActive: tab.id === newActiveTabId
        })),
        activeTabId: newActiveTabId
      };
    });
  }, []);

  const addMessageToTab = useCallback((tabId: string, message: MessageType) => {
    setTabsState(prev => ({
      ...prev,
      tabs: prev.tabs.map(tab =>
        tab.id === tabId
          ? { ...tab, messages: [...tab.messages, message] }
          : tab
      )
    }));
  }, []);

  const updateTabTitle = useCallback((tabId: string, title: string) => {
    setTabsState(prev => ({
      ...prev,
      tabs: prev.tabs.map(tab =>
        tab.id === tabId ? { ...tab, title } : tab
      )
    }));
  }, []);

  const updateTabConversationId = useCallback((tabId: string, conversationId: number) => {
    const newTabId = `conv-${conversationId}`;
    
    setTabsState(prev => {
      const isActiveTab = prev.activeTabId === tabId;
      
      return {
        ...prev,
        activeTabId: isActiveTab ? newTabId : prev.activeTabId,
        tabs: prev.tabs.map(tab =>
          tab.id === tabId 
            ? { 
                ...tab, 
                conversationId,
                id: newTabId, 
                title: tab.title || `Chat ${conversationId}`,
                isActive: isActiveTab 
              } 
            : tab
        )
      };
    });
  }, []);

  const updateTabBookingStatus = useCallback((tabId: string, bookingStatus: string) => {
    setTabsState(prev => ({
      ...prev,
      tabs: prev.tabs.map(tab =>
        tab.id === tabId
          ? { ...tab, bookingStatus }
          : tab
      )
    }));
  }, []);

  const getActiveTab = useCallback(() => {
    const activeTab = tabsState.tabs.find(tab => tab.id === tabsState.activeTabId);
    
    if (activeTab) {
      return activeTab;
    }
    
    const conversationTab = tabsState.tabs.find(tab => tab.type === 'conversation');
    return conversationTab || tabsState.tabs[0];
  }, [tabsState.tabs, tabsState.activeTabId]);

  useEffect(() => {
    const activeTab = tabsState.tabs.find(tab => tab.id === tabsState.activeTabId);
    
    if (!activeTab && tabsState.tabs.length > 0) {
      const conversationTab = tabsState.tabs.find(tab => tab.type === 'conversation');
      const fallbackTab = conversationTab || tabsState.tabs[0];
      
      console.warn('Invalid activeTabId detected, fixing to:', fallbackTab.id);
      setTabsState(prev => ({
        ...prev,
        activeTabId: fallbackTab.id,
        tabs: prev.tabs.map(tab => ({
          ...tab,
          isActive: tab.id === fallbackTab.id
        }))
      }));
    }
  }, [tabsState.tabs, tabsState.activeTabId]);

  const getTabMessages = useCallback((tabId: string) => {
    const tab = tabsState.tabs.find(t => t.id === tabId);
    return tab?.messages || [];
  }, [tabsState.tabs]);

  return {
    tabs: tabsState.tabs,
    activeTabId: tabsState.activeTabId,
    activeTab: getActiveTab(),
    isLoadingConversations,
    setActiveTab,
    createNewChatTab,
    closeTab,
    addMessageToTab,
    updateTabTitle,
    updateTabConversationId,
    updateTabBookingStatus,
    getTabMessages,
    refreshConversations: loadConversations
  };
}; 