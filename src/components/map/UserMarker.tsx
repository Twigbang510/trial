import useMapStore from "@/store/useMapStore";
import L from "leaflet";
import { Marker } from "react-leaflet";

const UserMarker = () => {
  const { userLocation } = useMapStore();

  if (!userLocation) {
    return null;
  }

  return (
    <Marker
      position={userLocation}
      icon={L.divIcon({
        className: "",
        html: "<div class='user-marker'></div>",
        iconSize: [30, 30],
        iconAnchor: [15, 15],
      })}
    />
  );
};

export default UserMarker;
