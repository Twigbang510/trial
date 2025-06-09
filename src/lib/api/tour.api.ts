import { PoiApiTourListResponse } from "@/types/poi.type";
import request from "@/lib/http.ts";

const tourApi = {
  getTour:  async (tourID:string = "6826e941438d7100713678b4",lang:string = "vi-south"):Promise<PoiApiTourListResponse> => {
    const res = await request.get(`/tours/${tourID}?lang=${lang}`)
    return res.data
  }
};

export default tourApi;