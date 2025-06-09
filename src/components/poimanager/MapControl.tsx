import { MapPin, Navigation } from "lucide-react";
import { PoiDrawer } from "./PoiDrawer";
import { Vertex } from "./types";

interface MapControlProps {
  onAddPoi: () => void;
  vertices: Vertex[];
  onRemovePoi: (id: string) => void;
  onClearAll: () => void;
  onSendPois: () => Promise<void>;
  isSending: boolean;
  onFocusLocation: () => void;
}

export function MapControl({
  onAddPoi,
  vertices,
  onRemovePoi,
  onClearAll,
  onSendPois,
  onFocusLocation,
}: MapControlProps) {
  return (
    <div
      style={{
        position: "absolute",
        top: "10px",
        right: "10px",
        zIndex: 100,
        padding: "10px",
        borderRadius: "5px",
      }}
    >
      <div
        style={{
          background: "white",
          padding: 20,
          borderRadius: 8,
          display: "flex",
          gap: 8,
        }}
      >
        <button
          onClick={onAddPoi}
          style={{
            marginRight: "5px",
            background: "lightblue",
            padding: 6,
            borderRadius: 4,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <MapPin size={16} /> Add POI
        </button>

        <button
          onClick={onFocusLocation}
          style={{
            marginRight: "5px",
            background: "#4CAF50",
            color: "white",
            padding: 6,
            borderRadius: 4,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <Navigation size={16} /> My Location
        </button>

        <PoiDrawer
          vertices={vertices}
          onRemovePoi={onRemovePoi}
          onClearAll={onClearAll}
          onSendPois={onSendPois}
        />
      </div>
    </div>
  );
}

