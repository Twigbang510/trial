import { useState } from 'react';

interface MapState {
  currentPosition: [number, number];
  setCurrentPosition: (position: [number, number]) => void;
  zoom: number;
  setZoom: (zoom: number) => void;
}

const useMapStore = (selector?: (state: MapState) => any) => {
  const [currentPosition, setCurrentPosition] = useState<[number, number]>([21.0285, 105.8542]);
  const [zoom, setZoom] = useState(13);
  
  const state = {
    currentPosition,
    setCurrentPosition,
    zoom,
    setZoom,
  };
  
  return selector ? selector(state) : state;
};

export default useMapStore; 