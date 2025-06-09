export interface Vertex {
  id: string;
  lat: number;
  lng: number;
  name: string;
}

export interface Edge {
  from: Vertex;
  to: Vertex;
  weight: number;
}

export interface PoiToAdd {
  id: string;
  lat: number;
  lng: number;
  name: string;
} 