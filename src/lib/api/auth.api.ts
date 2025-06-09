import { EStorageKey } from "@/constants/storage.ts";
import request from "@/lib/http.ts";
import { LocalStorage } from "@/lib/services/local-storage";
import { AuthResponse, LoginBody } from "@/types/auth.type.ts";
import { UserType } from "@/types/user.type.ts";

export const URL_LOGIN = "/auth/login";
export const URL_LOGOUT = "";
export const URL_REFRESH_TOKEN = "";
export const URL_SIGNUP = "/auth/register";
export const URL_ME = "/auth/me";
export const URL_SESSION_ACCESS_TOKEN = "/sessions/auth/access-token";
export const URL_SESSION_AUTH = "/sessions/auth/auth";

const authApi = {
  registerAccount(body: any) {
    return request.post<AuthResponse>(URL_SIGNUP, body);
  },
  async login(body: LoginBody) {
    const res = await request.post<AuthResponse>(URL_LOGIN, body);

    const {
      data: {
        accessToken: { accessToken: token, refreshToken },
      },
    } = res;

    LocalStorage.set(EStorageKey.AUTH_TOKEN, token);
    LocalStorage.set(EStorageKey.AUTH_REFRESHTOKEN, refreshToken);

    const user = await authApi.authMe();
    LocalStorage.set(EStorageKey.AUTH_USER, user);

    return user;
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
