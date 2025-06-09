import {SERVER_URL} from "@/config/app.ts";
import request from "@/lib/http.ts";

export const URL_MESSENGER_CONVERSATIONS = '/conversations';
export const URL_MESSENGER = '/api/webhook/facebook/sync';

const messengerApi = {
  getConversations: async (): Promise<any> => {
    const res = await request.get(URL_MESSENGER_CONVERSATIONS);
    return res.data;
  },

  getConversationDetail: async (conversationId: string) => {
    const res = await request.get(
      `${URL_MESSENGER_CONVERSATIONS}/${conversationId}`
    );
    return res.data;
  },

  getMessagesFromConversation: async (conversationId: string): Promise<any> => {
    const data = await messengerApi.getConversationDetail(conversationId);
    return data.messages;
  },

  switchHumanTakeover: async (conversationId: string) => {
    const res = await fetch(
      `${SERVER_URL}${URL_MESSENGER_CONVERSATIONS}/${conversationId}/switch`,
      {
        method: 'POST',
      }
    );
    return res.status === 200;

  },

  syncConversations: async (socialAppId?: string) => {
    const res = await fetch(`${SERVER_URL}${URL_MESSENGER}/${socialAppId}/sync`, {
      method: 'POST',
    });
    return res.status === 200;

  },
};

export default messengerApi;
