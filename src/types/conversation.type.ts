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