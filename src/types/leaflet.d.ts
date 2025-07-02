declare module 'leaflet' {
  export interface LatLngLiteral {
    lat: number;
    lng: number;
  }
  
  export type LatLngExpression = [number, number] | LatLngLiteral;
  export type LatLngTuple = [number, number];
  
  export interface LatLngBounds {
    _southWest: LatLngLiteral;
    _northEast: LatLngLiteral;
  }
  
  export interface Map {
    // Map interface
  }
  
  export interface DivIconOptions {
    html?: string;
    iconSize?: [number, number];
    className?: string;
    iconAnchor?: [number, number];
  }
  
  export interface DivIcon {
    // DivIcon interface
  }
  
  const L: {
    divIcon: (options: DivIconOptions) => DivIcon;
    // Add other L methods as needed
  };
  
  export default L;
} 