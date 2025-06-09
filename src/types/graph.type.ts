export interface Edge {
  from: string;
  to: string;
  weight: number;
}

export interface Neighbor {
  id: string;
  weight: number;
}

export type AdjacencyList = Map<string, Neighbor[]>;
