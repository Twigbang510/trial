import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { List, X } from "lucide-react";
import { Vertex } from "./types";

interface PoiDrawerProps {
  vertices: Vertex[];
  onRemovePoi: (id: string) => void;
  onClearAll: () => void;
  onSendPois: () => Promise<void>;
}

export function PoiDrawer({
  vertices,
  onRemovePoi,
  onClearAll,
  onSendPois,
}: PoiDrawerProps) {
  return (
    <Drawer>
      <DrawerTrigger asChild>
        <button
          style={{
            marginRight: "5px",
            background: "#f0f0f0",
            padding: 6,
            borderRadius: 4,
            display: "flex",
            alignItems: "center",
            gap: 4,
          }}
        >
          <List size={16} /> View POIs
        </button>
      </DrawerTrigger>
      <DrawerContent className="z-[100] max-h-screen">
        <DrawerHeader>
          <DrawerTitle>Saved Points of Interest</DrawerTitle>
        </DrawerHeader>

        {vertices.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            No POIs added yet. Add a POI at your current location.
          </div>
        ) : (
          <div className="p-4 space-y-2 overflow-y-auto" style={{ maxHeight: "calc(100vh - 180px)" }}>
            {vertices.map((poi) => (
              <div
                key={poi.id}
                className="p-3 border rounded-md flex justify-between items-center"
              >
                <div>
                  <div className="font-medium">{poi.name}</div>
                  <div className="text-sm text-gray-500">
                    ID: {poi.id} • Lat: {poi.lat.toFixed(6)} • Lng:{" "}
                    {poi.lng.toFixed(6)}
                  </div>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => onRemovePoi(poi.id)}
                >
                  <X size={16} />
                </Button>
              </div>
            ))}
          </div>
        )}

        <DrawerFooter>
          <Button variant="outline" onClick={onClearAll}>
            Clear All POIs
          </Button>
          <Button onClick={onSendPois}>Send POIs to server</Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
}

