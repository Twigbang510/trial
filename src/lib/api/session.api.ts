import { DOMAIN_URL } from "@/config/app";
import request from "@/lib/http.ts";
import { LocalStorage } from "../services/local-storage";

export interface AuthOnlineBody {
  charged_duration: number;
  money_amount: number;
  lang?: string;
  callback_url?: string;
}

export interface AuthOnlineResponse {
  paymentUrl: string;
}

export interface AuthSession {
  id: string;
}

export interface AuthGetAccessTokenResponse {
  pending: boolean;
  accessToken: string;
}

export const URL_SESSION = "/sessions";

const sessionApi = {
  //   async getAccounts(): Promise<AccountApiListResponse> {
  //     const res = await request.get<AccountApiListResponse>(URL_ACCOUNT);

  //     return res.data;
  //   }

  async auth(): Promise<AuthSession | undefined> {
    try {
      const res = await request.get<AuthSession>(`${URL_SESSION}/auth`);

      const data = res.data;
      return {
        id: data.id,
      };
    } catch (e: any) {
      const status = e.response.status;

      if (status == 403) {
        return undefined;
      }

      throw e;
    }
  },

  async authOnline({
    charged_duration,
    money_amount,
    lang = "vi",
    callback_url = `${DOMAIN_URL}/callback-online`,
  }: AuthOnlineBody): Promise<AuthOnlineResponse> {
    const res = await request.post(`${URL_SESSION}/auth/online`, {
      charged_duration,
      money_amount,
      lang,
      callback_url,
    });
    const data = res.data;

    return {
      paymentUrl: data.payment_url,
    };
  },

  async authOffline(): Promise<void> {},

  async getAccessToken(
    shortedAuthCode?: string
  ): Promise<AuthGetAccessTokenResponse | undefined> {
    let authCode;
    if (!shortedAuthCode) {
      authCode = LocalStorage.get("auth_code");
    } else {
      authCode = shortedAuthCode;
    }

    if (!authCode) {
      console.log("auth_code is empty");
      return undefined;
    }

    const res = await request.post(`${URL_SESSION}/auth/access-token`, {
      auth_code: authCode,
    });

    // payment is pending
    if (res.status === 202) {
      return {
        pending: true,
        accessToken: "",
      };
    }

    const data = res.data;
    return {
      pending: false,
      accessToken: data.access_token,
    };
  },
};

export default sessionApi;
