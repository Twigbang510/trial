import axios from "axios";
import { EStorageKey } from "@/constants/storage";
import { LocalStorage } from "@/lib/services/local-storage";
import { User, UserUpdate } from "@/types/user.type";
import { API_URL } from "@/config/app";

const AUTH_API_URL = `${API_URL}/api/v1/auth`;
const USER_API_URL = `${API_URL}/api/v1/users`;

export const URL_LOGIN = "/account/login";
export const URL_SIGNUP = "/account/register";
export const URL_LOGOUT = "/account/logout";
export const URL_REFRESH_TOKEN = "/account/refresh-token";
export const URL_SESSION_ACCESS_TOKEN = "/sessions/access-token";
export const URL_ME = "/account/me";
export const URL_SESSION_AUTH = "/sessions/auth/auth";

interface LoginRequest {
  email: string;
  password: string;
}

interface LoginResponse {
  access_token: string;
  user: User;
}

interface SignupRequest {
  email: string;
  password: string;
  full_name?: string;
  username?: string;
}

interface ForgotPasswordRequest {
  email: string;
}

interface VerifyCodeRequest {
  email: string;
  code: string;
}

interface ResetPasswordRequest {
  email: string;
  code: string;
  new_password: string;
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  try {
    const authStateStr = localStorage.getItem('auth_state');
    if (authStateStr) {
      const authState = JSON.parse(authStateStr);
      const token = authState.token;
      if (token) {
        return {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };
      }
    }
  } catch (error) {
    console.warn('Failed to get auth headers:', error);
  }
  return {
    'Content-Type': 'application/json'
  };
};

const authApi = {
  registerAccount(body: SignupRequest) {
    return axios.post(`${AUTH_API_URL}/signup`, body);
  },
  login(body: LoginRequest) {
    return axios.post<LoginResponse>(`${AUTH_API_URL}/signin`, body);
  },
  forgotPassword(data: ForgotPasswordRequest) {
    return axios.post(`${AUTH_API_URL}/forgot-password`, data);
  },
  verifyCode(data: VerifyCodeRequest) {
    return axios.post(`${AUTH_API_URL}/verify-code`, data);
  },
  resetPassword(data: ResetPasswordRequest) {
    return axios.post(`${AUTH_API_URL}/reset-password`, data);
  },
  getCurrentUser() {
    return axios.get<User>(`${USER_API_URL}/me`, {
      headers: getAuthHeaders()
    });
  },
  updateUser(data: UserUpdate) {
    return axios.put<User>(`${USER_API_URL}/me`, data, {
      headers: getAuthHeaders()
    });
  },
  logout() {
    // Clear the auth_state key used by authService
    localStorage.removeItem('auth_state');
    // Also clear old storage keys for backward compatibility
    LocalStorage.remove(EStorageKey.AUTH_TOKEN);
    LocalStorage.remove(EStorageKey.AUTH_REFRESHTOKEN);
    LocalStorage.remove(EStorageKey.AUTH_USER);
  },
};

export default authApi;
