import { CHATBOT_URL, SECONDS_IN_DAY, STAGING_SERVER_URL } from "@/config/app";
import { SERVER_URL } from "@/config/app.ts";
import HttpStatusCode from "@/constants/httpStatusCode.enum";
import {
  URL_LOGIN,
  URL_LOGOUT,
  URL_SESSION_ACCESS_TOKEN,
  URL_SIGNUP,
} from "@/lib/api/auth.api";
import { isAxiosUnauthorizedError } from "@/lib/axios.ts";
import { AuthResponse } from "@/types/auth.type";
import { ErrorResponse } from "@/types/utils.type";
import axios, { AxiosError, type AxiosInstance } from "axios";
import {
  clearLS,
  getAccessTokenFromLS,
  getRefreshTokenFromLS,
  setAccessTokenToLS,
  setRefreshTokenToLS,
} from "./auth";

export class Http {
  instance: AxiosInstance;
  private token: string;
  private refreshToken: string;

  constructor(baseUrl?: string) {
    const serverUrl = baseUrl
      ? baseUrl
      : process.env.NODE_ENV === "production"
      ? SERVER_URL
      : STAGING_SERVER_URL;
    console.log("Server URL: ", serverUrl, baseUrl);

    this.token = getAccessTokenFromLS();
    this.refreshToken = getRefreshTokenFromLS();
    this.instance = axios.create({
      baseURL: `${serverUrl}/api`,
      timeout: 10000,
      headers: {
        "Content-Type": "application/json",
        "expire-access-token": SECONDS_IN_DAY,
        "expire-refresh-token": SECONDS_IN_DAY * 160,
      },
    });
    this.instance.interceptors.request.use(
      (config) => {
        if (this.token && config.headers) {
          config.headers.authorization = `Bearer ${this.token}`;
          return config;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );
    // Add a response interceptor
    this.instance.interceptors.response.use(
      (response) => {
        const { url } = response.config;
        console.log({ url });
        if (url === URL_LOGIN || url === URL_SIGNUP) {
          const data = response.data as AuthResponse;
          this.token = data.accessToken.accessToken;
          this.refreshToken = data.accessToken.refreshToken;
          setAccessTokenToLS(this.token);
          setRefreshTokenToLS(this.refreshToken);
        } else if (url === URL_LOGOUT) {
          this.token = "";
          this.refreshToken = "";
          clearLS();
        } else if (url === URL_SESSION_ACCESS_TOKEN) {
          const data = response.data;
          this.token = data.access_token;
          setAccessTokenToLS(this.token);
        }
        return response;
      },
      (error: AxiosError) => {
        // Only toast errors which are not 422 and 401
        if (
          ![
            HttpStatusCode.UnprocessableEntity,
            HttpStatusCode.Unauthorized,
          ].includes(error.response?.status as number)
        ) {
          const data: any | undefined = error.response?.data;
          const message = data?.message || error.message;
          console.log(`Error ${message}`);
        }

        // Unauthorized (401) has many cases
        // - Token is not correct
        // - Token is not passed
        // - Token is expired

        // If 401
        if (
          isAxiosUnauthorizedError<
            ErrorResponse<{ name: string; message: string }>
          >(error)
        ) {
          // const config = error.response?.config;
          // If Token is expired and that request does not belong to the request refresh token
          // we will call refresh token
          // if (
          //   isAxiosExpiredTokenError(error) &&
          //   config?.url !== URL_REFRESH_TOKEN
          // ) {
          //   // Try not to call handleRefreshToken twice
          //   this.refreshTokenRequest = this.refreshTokenRequest
          //     ? this.refreshTokenRequest
          //     : this.handleRefreshToken().finally(() => {
          //         setTimeout(() => {
          //           this.refreshTokenRequest = null;
          //         }, 10000);
          //       });
          //   return this.refreshTokenRequest.then((token) => {
          //     return this.instance({
          //       ...config,
          //       headers: { ...config?.headers, authorization: token },
          //     });
          //   });
          // }

          // If token is not correct or is not passed or expired but failed to call the refresh token
          // we will clear the local storage and toast

          clearLS();
          this.token = "";
          this.refreshToken = "";
          console.log(
            `Error ${
              error.response?.data.data?.message || error.response?.data.message
            }`
          );
          // window.location.reload()
        }
        return Promise.reject(error);
      }
    );
  }

  // private handleRefreshToken() {
  //   return this.instance
  //     .post<RefreshTokenResponse>(URL_REFRESH_TOKEN, {
  //       refresh_token: this.refreshToken,
  //     })
  //     .then((res) => {
  //       const { token } = res.data.data;
  //       setAccessTokenToLS(token);
  //       this.token = token;
  //       return token;
  //     })
  //     .catch((error) => {
  //       clearLS();
  //       this.token = "";
  //       this.refreshToken = "";
  //       throw error;
  //     });
  // }
}

const request = new Http().instance;
export const chatbotRequest = new Http(CHATBOT_URL).instance;
export default request;
