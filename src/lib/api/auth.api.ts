import axios from "axios";
import { EStorageKey } from "@/constants/storage.ts";
import request from "@/lib/http.ts";
import { LocalStorage } from "@/lib/services/local-storage";
// import { AuthResponse, LoginBody } from "@/types/auth.type.ts";
import { UserType } from "@/types/user.type.ts";
import { API_URL } from "@/config/app";

const AUTH_API_URL = `${API_URL}/api/v1/auth`;

export const URL_LOGIN = "/auth/login";
export const URL_LOGOUT = "";
export const URL_REFRESH_TOKEN = "";
export const URL_SIGNUP = "/auth/register";
export const URL_ME = "/auth/me";
export const URL_SESSION_ACCESS_TOKEN = "/sessions/auth/access-token";
export const URL_SESSION_AUTH = "/sessions/auth/auth";

const authApi = {
  registerAccount(body: { email: string; password: string; full_name: string; username: string }) {
    console.log(body);
    return axios.post(`${AUTH_API_URL}/signup`, body);
  },
  login(body: { email: string; password: string }) {
    return axios.post(`${AUTH_API_URL}/signin`, body);
  },
  forgotPassword(email: string) {
    return axios.post(`${AUTH_API_URL}/forgot-password`, { email });
  },
  verifyCode(email: string, code: string) {
    return axios.post(`${AUTH_API_URL}/verify-code`, { email, code });
  },
  resetPassword(email: string, new_password: string) {
    return axios.post(`${AUTH_API_URL}/reset-password`, { email, new_password });
  },
  logout() {
    LocalStorage.remove(EStorageKey.AUTH_TOKEN);
    LocalStorage.remove(EStorageKey.AUTH_REFRESHTOKEN);
    LocalStorage.remove(EStorageKey.AUTH_USER);
  },
  async authMe() {
    const res = await request.get<UserType>(URL_ME);
    return res.data;
  },
};

export default authApi;
