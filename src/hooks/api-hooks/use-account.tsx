import {useQuery, UseQueryOptions} from '@tanstack/react-query';
import accountApi from "@/lib/api/account.api.ts";
import {AccountApiListResponse} from "@/types/account.type.ts";

export const useAccountQuery = (options?: Omit<UseQueryOptions<AccountApiListResponse>, 'queryKey' | 'queryFn'>) => {
  return useQuery<AccountApiListResponse>({
    ...options,
    queryKey: ['profile'],
    queryFn: accountApi.getAccounts,
  })
}