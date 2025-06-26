import { API_URL } from "@/config/app";
import { useMutation, useQuery } from "@tanstack/react-query";
import axios from "axios";

interface PoiRequest {
  name: string;
  position: {
    lat: number;
    lng: number;
  };
}

export interface PoiResponse {
  id: string;
  name: string;
  position: {
    lat: number;
    lng: number;
  };
  localizedData?: {
    name: string;
    description: {
      text: string;
      audio: string;
    };
  };
}

export const useCreatePois = () => {
  return useMutation({
    mutationFn: async (pois: PoiRequest[]) => {
      const response = await axios.post(
        `${API_URL}/api/pois/basic`,
        pois
      );
      return response.data;
    },
  });
};

export const useGetPois = () => {
  return useQuery({
    queryKey: ["pois"],
    queryFn: async () => {
      const response = await axios.get<PoiResponse[]>(
        `${API_URL}/api/pois`,
        {
          params: {
            lang: "vi-south"
          },
          headers: {
            "Content-Type": "application/json",
          }
        }
      );
      return response.data;
    },
    refetchOnMount: true,
    refetchOnWindowFocus: true,
    gcTime: 0,
    staleTime: 0
  });
}; 