export type ConversationDetailResponse = {
  id: string;
  status: string;
  socialAppId: string;
  contactId: string;
  humanTakeover: boolean;
  startedAt: string;
  contact: {
    id: string;
    name: string;
  };
};

export type ConversationsResponse =
  Array<ConversationDetailResponse>;

export interface MessageType {
  id: string;
  content: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  isAppropriate?: boolean;
}

export interface ConversationType {
  id: number;
  title: string;
  context: string;
  created_at: string;
}

export interface ChatTab {
  id: string;
  title: string;
  conversationId?: number;
  messages: MessageType[];
  isActive: boolean;
  type: 'new-chat' | 'conversation' | 'career-explorer';
}

export interface ChatTabsState {
  tabs: ChatTab[];
  activeTabId: string;
}

export interface ChatApiResponse {
  response: string;
  conversation_id: number;
  is_appropriate: boolean;
  moderation_action?: 'CLEAN' | 'WARNING' | 'BLOCKED';
  warning_message?: string;
}

export interface ConversationApiResponse {
  id: number;
  title: string;
  context: string;
  created_at: string;
  updated_at?: string;
  messages: {
    id: number;
    content: string;
    sender: string;
    is_appropriate: boolean;
    created_at: string;
  }[];
}