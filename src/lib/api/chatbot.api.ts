import { chatbotRequest } from "../http";

export const URL_LOGIN = "/auth/login";
export const URL_LOGOUT = "";
export const URL_REFRESH_TOKEN = "";
export const URL_SIGNUP = "/auth/register";
export const URL_ME = "/auth/me";
export const URL_SESSION_ACCESS_TOKEN = "/sessions/auth/access-token";
export const URL_SESSION_AUTH = "/sessions/auth/auth";

const chatbotApi = {
  getClientId: async (): Promise<string | undefined> => {
    try {
      const response = await chatbotRequest.get("/getClientId");
      return response.data.client_id;
    } catch (error) {
      console.error("Error fetching client ID:", error);
      return undefined;
    }
  },
  chat: async (
    query: string,
    clientId: string
  ): Promise<{ content: string }> => {
    try {
      const response = await chatbotRequest.post(
        "/ask",
        {
          user_query: query,
          voice_code: "vi-VN",
          enable_suggestion: true,
        },
        {
          headers: {
            ClientId: clientId,
          },
        }
      );
      return {
        content: response.data?.assistant_reply?.content || "",
      };
    } catch (error) {
      console.log("Error in chatbot API:", error);
      return {
        content: "Sorry, I couldn't process your request.",
      };
    }
  },
};

export default chatbotApi;
