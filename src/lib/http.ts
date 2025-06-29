import { CHATBOT_URL, SECONDS_IN_DAY, API_URL } from "@/config/app";
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
// import { EStorageKey } from "@/constants/storage";
// import { LocalStorage } from "@/lib/services/local-storage";

export class Http {
  instance: AxiosInstance;
  private token: string;
  private refreshToken: string;

  constructor(baseUrl?: string) {
    const serverUrl = baseUrl
      ? baseUrl
      : API_URL;

    this.token = getAccessTokenFromLS() || "";
    this.refreshToken = getRefreshTokenFromLS() || "";
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
        // Priority: Get token from auth_state (new system)
        try {
          const authStateStr = localStorage.getItem('auth_state');
          if (authStateStr) {
            const authState = JSON.parse(authStateStr);
            const token = authState.token;
            if (token && config.headers) {
              config.headers.Authorization = `Bearer ${token}`;
              return config;
            }
          }
        } catch (error) {
          console.log('Error parsing auth_state:', error);
        }
        
        // Fallback: Use old token method for backward compatibility
        if (this.token && config.headers) {
          config.headers.Authorization = `Bearer ${this.token}`;
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
        
        // Simplified response handling - let authService handle auth state
        if (url === URL_SESSION_ACCESS_TOKEN) {
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
          // Clear auth data and let authService handle logout
          
          // Clear old storage
          clearLS();
          this.token = "";
          this.refreshToken = "";
          
          // Clear new storage and trigger auth change
          localStorage.removeItem('auth_state');
          window.dispatchEvent(new Event('auth-change'));
          
          console.log(
            `Unauthorized error: ${
              error.response?.data.data?.message || error.response?.data.message
            }`
          );
        }
        return Promise.reject(error);
      }
    );
  }

}

const request = new Http().instance;
export const chatbotRequest = new Http(CHATBOT_URL).instance;
export default request;
