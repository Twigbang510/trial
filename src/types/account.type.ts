import {PayloadSuccessResponse} from "@/types/utils.type.ts";

export interface AccountApiItem {
  id: string
  userId: string
  accountName: string
  createdAt: string
  chatbotUrl: string
}

export type AccountApiListResponse = PayloadSuccessResponse<AccountApiItem[]>