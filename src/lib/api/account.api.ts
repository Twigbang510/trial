import request from "@/lib/http.ts";
import {AccountApiListResponse} from "@/types/account.type.ts";

export const URL_ACCOUNT = '/account';

const accountApi = {
  async getAccounts(): Promise<AccountApiListResponse> {
    const res = await request.get<AccountApiListResponse>(URL_ACCOUNT);

    return res.data;
  }

}

export default accountApi