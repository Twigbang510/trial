import {SuccessResponse} from "@/types/utils.type.ts";

export interface LoginBody {
  email: string;
  password: string;
}

export type AuthResponse = {
  accessToken: {
    accessToken: string;
    refreshToken: string;
  };
}

export type RefreshTokenResponse = SuccessResponse<{ token: string }>