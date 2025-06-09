import { AdjacencyList, Edge, Neighbor } from "@/types/graph.type";
import { PoiCoordinates } from "@/types/poi.type";
import { LatLngExpression } from "leaflet";
import { PriorityQueue } from "./priority-queue";

export class EdgeWeightedGraph {
  private adjacencyList: AdjacencyList;
  private coordMap: Map<string, PoiCoordinates>;
  private pois: PoiCoordinates[];

  constructor(edges: Edge[], pois: PoiCoordinates[]) {
    this.pois = pois;
    this.adjacencyList = this.buildAdjacencyList(edges);
    this.coordMap = new Map(pois.map((poi) => [poi.id, poi]));
  }

  private buildAdjacencyList(edges: Edge[]): AdjacencyList {
    const adjacencyList = new Map<string, Neighbor[]>();

    // Initialize nodes
    edges.forEach((edge) => {
      if (!adjacencyList.has(edge.from)) adjacencyList.set(edge.from, []);
      if (!adjacencyList.has(edge.to)) adjacencyList.set(edge.to, []);
    });

    // Add bidirectional edges
    edges.forEach((edge) => {
      adjacencyList.get(edge.from)?.push({ id: edge.to, weight: edge.weight });
      adjacencyList.get(edge.to)?.push({ id: edge.from, weight: edge.weight });
    });

    return adjacencyList;
  }

  public findNearestPOIPoint(
    input: LatLngExpression,
    useHaversine: boolean = true,
  ): PoiCoordinates | null {
    if (this.pois.length === 0) return null;

    let inputLat: number, inputLng: number;
    if (Array.isArray(input)) {
      [inputLat, inputLng] = input;
    } else {
      inputLat = input.lat;
      inputLng = input.lng;
    }

    let nearestPoi: PoiCoordinates | null = null;
    let minDistance = Infinity;

    for (const poi of this.pois) {
      const distance = useHaversine
        ? this.haversineDistance(inputLat, inputLng, poi.lat, poi.lng)
        : this.euclideanDistance(inputLat, inputLng, poi.lat, poi.lng);

      if (distance < minDistance) {
        minDistance = distance;
        nearestPoi = poi;
      }
    }

    return nearestPoi ? { ...nearestPoi } : null;
  }

  public findShortestPath(startId: string, endId: string): PoiCoordinates[] {
    if (!this.adjacencyList.has(startId) || !this.adjacencyList.has(endId)) {
      return [];
    }
    const distances = new Map<string, number>();
    const predecessors = new Map<string, string | null>();
    const pq = new PriorityQueue();

    // Initialize distances
    this.adjacencyList.forEach((_, key) => {
      distances.set(key, Infinity);
      predecessors.set(key, null);
    });

    distances.set(startId, 0);
    pq.enqueue(startId, 0);

    while (!pq.isEmpty()) {
      const current = pq.dequeue()!;
      if (!current) break;

      const [currentId, currentDist] = current;

      if (currentDist > distances.get(currentId)!) continue;

      if (currentId === endId) {
        return this.reconstructPath(predecessors, endId);
      }

      this.adjacencyList.get(currentId)?.forEach((neighbor) => {
        const newDist = currentDist + neighbor.weight;
        if (newDist < distances.get(neighbor.id)!) {
          distances.set(neighbor.id, newDist);
          predecessors.set(neighbor.id, currentId);
          pq.enqueue(neighbor.id, newDist);
        }
      });
    }

    return [];
  }

  private reconstructPath(
    predecessors: Map<string, string | null>,
    endId: string,
  ): PoiCoordinates[] {
    const path: PoiCoordinates[] = [];
    let currentId: string | null = endId;

    while (currentId !== null) {
      const poi = this.coordMap.get(currentId);
      if (poi) path.unshift(poi);
      currentId = predecessors.get(currentId) ?? null;
    }

    return path;
  }

  private haversineDistance(
    lat1: number,
    lng1: number,
    lat2: number,
    lng2: number,
  ): number {
    const R = 6371e3; // Radius of Earth in meters

    const phi1 = (lat1 * Math.PI) / 180;
    const phi2 = (lat2 * Math.PI) / 180;
    const deltaPhi = ((lat2 - lat1) * Math.PI) / 180;
    const deltaLambda = ((lng2 - lng1) * Math.PI) / 180;

    const a =
      Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
      Math.cos(phi1) *
        Math.cos(phi2) *
        Math.sin(deltaLambda / 2) *
        Math.sin(deltaLambda / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in meters
  }

  private euclideanDistance(
    lat1: number,
    lng1: number,
    lat2: number,
    lng2: number,
  ): number {
    const deltaLat = lat2 - lat1;
    const deltaLng = lng2 - lng1;
    return Math.sqrt(deltaLat * deltaLat + deltaLng * deltaLng); // Distance in degrees
  }
}
