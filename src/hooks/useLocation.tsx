import useMapStore from "@/store/useMapStore";
import { useEffect } from "react";
import { toast } from "sonner";

export const useLocation = () => {
  const { setUserLocation, setError } = useMapStore();

  useEffect(() => {
    if (!navigator.geolocation) {
      toast.error("Geolocation is not supported by your browser");
      return;
    }

    navigator.permissions?.query({ name: "geolocation" }).then((result) => {
      if (result.state === "denied") {
        toast.error("Please enable location access in your browser settings");
        return;
      }

      if (result.state === "prompt") {
        navigator.geolocation.getCurrentPosition(
          () => {},
          () => {},
        );
      }
    });

    const watchId = navigator.geolocation.watchPosition(
      (pos) => {
        setUserLocation({
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
        });
      },
      (err) => {
        let errorMessage = "Cannot get your location";

        switch (err.code) {
          case err.PERMISSION_DENIED:
            errorMessage = "Please allow location access to use this feature";
            break;
          case err.POSITION_UNAVAILABLE:
            errorMessage = "Location information is unavailable";
            break;
          case err.TIMEOUT:
            errorMessage = "Location request timed out";
            break;
        }

        toast.error(errorMessage);
        setError(errorMessage);
      },
      {
        enableHighAccuracy: true,
        maximumAge: 0,
        timeout: 30000,
      },
    );

    return () => navigator.geolocation.clearWatch(watchId);
  }, []);
};
