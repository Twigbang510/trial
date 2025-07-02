import { useState } from 'react';

interface TourState {
  graph: any;
  isStartTour: boolean;
  typeTour: string;
  currentVisitPoint: any;
  setStartTour: (start: boolean) => void;
  setTypeTour: (type: string) => void;
  setCurrentVisitPoint: (point: any) => void;
}

const useTourStore = (selector?: (state: TourState) => any) => {
  const [graph, setGraph] = useState(null);
  const [isStartTour, setStartTour] = useState(false);
  const [typeTour, setTypeTour] = useState('');
  const [currentVisitPoint, setCurrentVisitPoint] = useState(null);
  
  const state = {
    graph,
    isStartTour,
    typeTour,
    currentVisitPoint,
    setStartTour,
    setTypeTour,
    setCurrentVisitPoint,
  };
  
  return selector ? selector(state) : state;
};

export default useTourStore; 