import { LatLngLiteral } from "leaflet";
export interface PoiApiItem {
  id: string;
  banner: string;
  thumbnail: string;
  range: number;
  localizedData: {
    name: string;
    description: {
      text: string;
      audio: string;
    };
  };
  position: {
    lat: number;
    lng: number;
  };
}
export type PoiCoordinates = Pick<PoiApiItem,"id"> & LatLngLiteral

export type PoiApiListResponse = PoiApiItem[];

export type PoiApiTour = {
  "tour_point": PoiApiItem,
  "order":number,
  "tour_point_id": string,
  "id_tour": string
}

export type PoiApiTourListResponse = PoiApiTour[]

