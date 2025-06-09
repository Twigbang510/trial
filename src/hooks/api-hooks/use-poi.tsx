import { useQuery, UseQueryOptions } from "@tanstack/react-query";
import poiApi from "@/lib/api/poi.api";
import { PoiApiListResponse } from "@/types/poi.type";

export const usePoiQuery = (
  langKey: string,
  accessToken: string,
  options?: Omit<UseQueryOptions<PoiApiListResponse>, "queryKey" | "queryFn">,
) => {
  return useQuery<PoiApiListResponse>({
    ...options,
    queryKey: ["pois", langKey],
    queryFn: () => poiApi.getPois(langKey, accessToken),
  });
};
