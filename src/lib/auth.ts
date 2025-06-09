import { LocalStorage } from "@/lib/services/local-storage.ts";
import { EStorageKey } from "@/constants/storage.ts";

export const LocalStorageEventTarget = new EventTarget();

export const setAccessTokenToLS = (accessToken: string) => {
  LocalStorage.set(EStorageKey.AUTH_TOKEN, accessToken);
};

export const setRefreshTokenToLS = (refresh_token: string) => {
  LocalStorage.set(EStorageKey.AUTH_REFRESHTOKEN, refresh_token);
};

export const clearLS = () => {
  console.log("clearLS");
  LocalStorage.remove(EStorageKey.AUTH_TOKEN);
  LocalStorage.remove(EStorageKey.AUTH_CODE);
  LocalStorage.remove(EStorageKey.AUTH_REFRESHTOKEN);
  LocalStorage.remove(EStorageKey.AUTH_USER);
  const clearLSEvent = new Event("clearLS");
  LocalStorageEventTarget.dispatchEvent(clearLSEvent);
};

export const getAccessTokenFromLS = () =>
  LocalStorage.get(EStorageKey.AUTH_TOKEN) || undefined;

export const getRefreshTokenFromLS = () =>
  LocalStorage.get(EStorageKey.AUTH_REFRESHTOKEN) || undefined;

export const getProfileFromLS = () => {
  const result = LocalStorage.get(EStorageKey.AUTH_USER);
  return result ? JSON.parse(result) : null;
};
