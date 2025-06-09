import request from "@/lib/http.ts";

export const URL_POI = "/pois";

const poiApi = {
  getPois: async (langKey: string, accessToken: string): Promise<any> => {
    const res = await request.get(`${URL_POI}?lang=${langKey}`, {
      headers: {
        "access-token": accessToken,
      },
    });
    return res.data;
  },
};

export default poiApi;
