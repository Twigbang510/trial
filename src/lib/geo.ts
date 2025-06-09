import { PoiApiListResponse } from "@/types/poi.type";

const EARTH_RADIUS_METERS = 6371e3;

export function calculateDistance(
  [lat1, lng1]: [number, number],
  [lat2, lng2]: [number, number],
): number {
  const lat1Rad = (lat1 * Math.PI) / 180;
  const lat2Rad = (lat2 * Math.PI) / 180;
  const deltaLat = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLng = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(deltaLng / 2) ** 2;

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS_METERS * c;
}

export const isWithinRadius = (
  userLat: number,
  userLng: number,
  poi: { lat: number; lng: number },
  radiusMeters: number,
) => {
  const userLatRad = (userLat * Math.PI) / 180;
  const poiLatRad = (poi.lat * Math.PI) / 180;
  const deltaLat = ((poi.lat - userLat) * Math.PI) / 180;
  const deltaLng = ((poi.lng - userLng) * Math.PI) / 180;

  const a =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(userLatRad) * Math.cos(poiLatRad) * Math.sin(deltaLng / 2) ** 2;

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS_METERS * c <= radiusMeters;
};

export const calculateUserDistance = (
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number,
): number => {
  const lat1Rad = (lat1 * Math.PI) / 180;
  const lat2Rad = (lat2 * Math.PI) / 180;
  const deltaLat = ((lat2 - lat1) * Math.PI) / 180;
  const deltaLng = ((lng2 - lng1) * Math.PI) / 180;

  const a =
    Math.sin(deltaLat / 2) ** 2 +
    Math.cos(lat1Rad) * Math.cos(lat2Rad) * Math.sin(deltaLng / 2) ** 2;

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return EARTH_RADIUS_METERS * c;
};

export const findCurrentPOIs = (
  userLat: number,
  userLng: number,
  pois: PoiApiListResponse,
) => {
  return (
    pois
      .map((poi) => ({
        ...poi,
        distance: calculateUserDistance(
          userLat,
          userLng,
          poi.position.lat,
          poi.position.lng,
        ),
      }))
      //.filter((poi) => poi.distance <= poi.range)
      .sort((a, b) => a.distance - b.distance)
  );
};
