import { LatLngBounds } from "leaflet";

// Pagoda coordinates
export const PAGODA_POSITION = [16.035451, 108.2241706];

const BOUNDS_BUFFER = 0.003; // 300 meters in degrees
export const PAGODA_BOUNDS = new LatLngBounds(
  [PAGODA_POSITION[0] - BOUNDS_BUFFER, PAGODA_POSITION[1] - BOUNDS_BUFFER],
  [PAGODA_POSITION[0] + BOUNDS_BUFFER, PAGODA_POSITION[1] + BOUNDS_BUFFER],
);

export const DUMMY_USER_LOCATION = {
  lat: 16.100178,
  lng: 108.278316,
};

export const LINHUNG_PAGODA_COMPONENTS = [
  {
    id: "1",
    name: "Cong? Chua`",
    range: 10,
    coordinates: {
      lat: 16.099636,
      lng: 108.277578,
    },
  },
  {
    id: "2",
    name: "Quan The Am Phat Dai",
    range: 15,
    coordinates: {
      lat: 16.099636,
      lng: 108.277002,
    },
  },
  {
    id: "3",
    name: "Thap Xa Loi",
    range: 20,
    coordinates: {
      lat: 16.099888,
      lng: 108.280087,
    },
  },
  {
    id: "4",
    name: "Vuon Loc Uyen",
    range: 10,
    coordinates: {
      lat: 16.09987,
      lng: 108.279112,
    },
  },
  {
    id: "6",
    name: "Vuon Lam Ti Ni",
    range: 10,
    coordinates: {
      lat: 16.100807,
      lng: 108.277368,
    },
  },
  {
    id: "7",
    name: "Restroom",
    range: 2,
    coordinates: {
      lat: 16.100613,
      lng: 108.276818,
    },
  },
  {
    id: "8",
    name: "Chanh dien",
    range: 20,
    coordinates: {
      lat: 16.1002,
      lng: 108.277798,
    },
  },
];
