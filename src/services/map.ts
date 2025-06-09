//import { Edge } from "@/types/graph.type";
//import { PoiCoordinates } from "@/types/poi.type";
//import { LatLngExpression } from "leaflet";
//// Define the POI coordinate type
//
//// Haversine formula to calculate distance between two lat/lng points (in meters)
//function haversineDistance(
//  lat1: number,
//  lng1: number,
//  lat2: number,
//  lng2: number
//): number {
//  const R = 6371e3; // Earth's radius in meters
//  const φ1 = (lat1 * Math.PI) / 180; // Convert to radians
//  const φ2 = (lat2 * Math.PI) / 180;
//  const Δφ = ((lat2 - lat1) * Math.PI) / 180;
//  const Δλ = ((lng2 - lng1) * Math.PI) / 180;
//
//  const a =
//    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
//    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2);
//  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
//
//  return R * c; // Distance in meters
//}
//
//// Euclidean distance (approximation for small areas, in degrees)
//function euclideanDistance(
//  lat1: number,
//  lng1: number,
//  lat2: number,
//  lng2: number
//): number {
//  const Δlat = lat2 - lat1;
//  const Δlng = lng2 - lng1;
//  return Math.sqrt(Δlat * Δlat + Δlng * Δlng); // Distance in degrees
//}
//
//// Function to find the nearest POI
//export function findNearestPOIPoint(
//  input: LatLngExpression,
//  pois: PoiCoordinates[],
//  useHaversine: boolean = true // Toggle between Haversine and Euclidean
//): PoiCoordinates | null {
//  if (pois.length === 0) return null;
//
//  // Extract lat/lng from LatLngExpression
//  let inputLat: number;
//  let inputLng: number;
//
//  if (Array.isArray(input)) {
//    [inputLat, inputLng] = input;
//  } else {
//    inputLat = (input as { lat: number; lng: number }).lat;
//    inputLng = (input as { lat: number; lng: number }).lng;
//  }
//
//  let nearestPoi: PoiCoordinates | null = null;
//  let minDistance = Infinity;
//
//  for (const poi of pois) {
//    const distance = useHaversine
//      ? haversineDistance(inputLat, inputLng, poi.lat, poi.lng)
//      : euclideanDistance(inputLat, inputLng, poi.lat, poi.lng);
//
//    if (distance < minDistance) {
//      minDistance = distance;
//      nearestPoi = poi;
//    }
//  }
//
//  if (nearestPoi) {
//    return {
//      ...nearestPoi,
//    };
//  }
//
//  return null;
//}
//
//
//// set up althogigm path
//
//// Adjacency list representation
//interface Neighbor {
//  id: string;
//  weight: number;
//}
//
//type AdjacencyList = Map<string, Neighbor[]>;
//
//// Simple Priority Queue for Dijkstra's algorithm
//class PriorityQueue {
//  private values: { id: string; priority: number }[] = [];
//
//  enqueue(id: string, priority: number) {
//    this.values.push({ id, priority });
//    this.sort();
//  }
//
//  dequeue(): { id: string; priority: number } | undefined {
//    return this.values.shift();
//  }
//
//  sort() {
//    this.values.sort((a, b) => a.priority - b.priority);
//  }
//
//  isEmpty(): boolean {
//    return this.values.length === 0;
//  }
//}
//
//// Build adjacency list from weightTwoPOI
//function buildAdjacencyList(edges: Edge[]): AdjacencyList {
//  const adjList = new Map<string, Neighbor[]>();
//
//  // Initialize empty neighbor arrays for all POIs
//  for (const edge of edges) {
//    if (!adjList.has(edge.from)) adjList.set(edge.from, []);
//    if (!adjList.has(edge.to)) adjList.set(edge.to, []);
//  }
//
//  // Add edges (undirected)
//  for (const edge of edges) {
//    adjList.get(edge.from)!.push({ id: edge.to, weight: edge.weight });
//    adjList.get(edge.to)!.push({ id: edge.from, weight: edge.weight });
//  }
//
//  return adjList;
//}
//
//// Find shortest path using Dijkstra's algorithm
//export function findShortestPath(
//  startPoi: PoiCoordinates,
//  endPoi: PoiCoordinates,
//  weightTwoPOI: Edge[],
//  poiCoordinates: PoiCoordinates[]
//): PoiCoordinates[] {
//  // Build adjacency list
//  const graph = buildAdjacencyList(weightTwoPOI);
//
//  // Create coordinate map for O(1) lookup
//  const coordMap = new Map<string, PoiCoordinates>(
//    poiCoordinates.map((poi) => [poi.id, poi])
//  );
//
//  // Validate inputs
//  if (!graph.has(startPoi.id) || !graph.has(endPoi.id)) {
//    return []; // Start or end POI not found
//  }
//
//  // Initialize data structures
//  const distances: { [key: string]: number } = {};
//  const predecessors: { [key: string]: string | null } = {};
//  const visited: Set<string> = new Set();
//  const pq = new PriorityQueue();
//
//  // Set initial distances
//  for (const poi of graph.keys()) {
//    distances[poi] = Infinity;
//    predecessors[poi] = null;
//  }
//  distances[startPoi.id] = 0;
//
//  // Start with startPoi
//  pq.enqueue(startPoi.id, 0);
//
//  // Dijkstra's algorithm
//  while (!pq.isEmpty()) {
//    const current = pq.dequeue();
//    if (!current) break;
//
//    const { id: currentPoi, priority: currentDistance } = current;
//
//    // Skip if visited or distance is outdated
//    if (visited.has(currentPoi) || currentDistance > distances[currentPoi]) {
//      continue;
//    }
//
//    // Mark as visited
//    visited.add(currentPoi);
//
//    // If endPoi reached, reconstruct path
//    if (currentPoi === endPoi.id) {
//      const path: PoiCoordinates[] = [];
//      let current: string | null = endPoi.id;
//      while (current !== null) {
//        const poi = coordMap.get(current);
//        if (poi) path.push(poi);
//        current = predecessors[current];
//      }
//      return path.reverse(); // Start -> end order
//    }
//
//    // Process neighbors
//    const neighbors = graph.get(currentPoi) || [];
//    for (const neighbor of neighbors) {
//      const neighborPoi = neighbor.id;
//      const weight = neighbor.weight;
//
//      if (visited.has(neighborPoi)) continue;
//
//      const newDistance = distances[currentPoi] + weight;
//
//      if (newDistance < distances[neighborPoi]) {
//        distances[neighborPoi] = newDistance;
//        predecessors[neighborPoi] = currentPoi;
//        pq.enqueue(neighborPoi, newDistance);
//      }
//    }
//  }
//
//  // No path found
//  return [];
//}

