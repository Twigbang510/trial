import { MapContainer, TileLayer, Marker, Polyline } from "react-leaflet";
import L, { LatLngExpression, Map, type LatLngTuple } from "leaflet";
import "leaflet/dist/leaflet.css";
import { PAGODA_BOUNDS, PAGODA_POSITION } from "@/constants/locations";
import { useLocation } from "@/hooks/useLocation";
import { renderToString } from "react-dom/server";
import { forwardRef, useEffect, useMemo, useState } from "react";
import useMapStore from "@/store/useMapStore";
import useGlobalStore from "@/store/useGlobalStore";
import { PoiApiTour, PoiApiTourListResponse, PoiCoordinates } from "@/types/poi.type";
import tourApi from "@/lib/api/tour.api";
import useTourStore from "@/store/useTourStore";
import useTourPoint from "@/hooks/useTourPoint";
import UserMarker from "../map/UserMarker";
import { CustomMarkerIcon } from "../map/CustomMarkerIcon";
import TourPointMarkerBeforeTour from "./TourPointMarkerBeforeTour";
import { usePoiQuery } from "@/hooks/api-hooks/use-poi";
import { TOUR_ID_DEFAULT } from "@/config/app";
import LeadMarker from "./LeadMarker";

declare module "react-leaflet" {
  export interface TileLayerProps {
    edgeBufferTiles: number;
  }
}

interface ITourMap {
  onPressPoi: (openState?: boolean) => void;
}


const TourMap = forwardRef(
  (_props: ITourMap, ref: React.Ref<Map>) => {
    useLocation();
    const {
      userLocation,
    } = useMapStore();
    const {selectedLanguageCode} = useGlobalStore();
    const {isNear} = useTourPoint()
    const {graph, isStartTour, setCurrentVisitPoint} = useTourStore(state=>state)

    const {data: poiData} = usePoiQuery(selectedLanguageCode, "");
    const [pathTour,setPathTour] = useState<LatLngExpression[]>()
    const [path, setPath] = useState<LatLngExpression[]>();
    const [tour,setTour] = useState<PoiApiTourListResponse>()
    const [arrIndexTourPoint,setArrIndexTourPoint] = useState<number[]>()


    // handle draw map
    const drawPathToNextPointInTour = () => {
      let path = null
      const currentVisitedPoint = getCurrentVisitPoint
        if(currentVisitedPoint && userLocation){
          const nearestPOItoMarker = graph.findNearestPOIPoint([
          currentVisitedPoint.tour_point.position.lat,
          currentVisitedPoint.tour_point.position.lng,
        ]);
        const nearestPOItoUser = graph.findNearestPOIPoint(userLocation, true);

        if (nearestPOItoMarker && nearestPOItoUser) {
          const middlePath: LatLngExpression[] = graph
            .findShortestPath(nearestPOItoUser.id, nearestPOItoMarker.id)
            .map((curr: PoiCoordinates) => [curr.lat, curr.lng]);
          path = [
            userLocation,
            ...middlePath
          ]
          } 
        return path
      }
    }
    const drawTour = (data:PoiApiTourListResponse) => {
    if (!data) return;
    const destinationList = data.map(curr => ({
      lat: curr.tour_point.position.lat,
      lng: curr.tour_point.position.lng,
    }));
    const arrIndexPoint:number[] = [0]
    let tourPath: LatLngExpression[] = [];
    for (let index = 0; index < destinationList.length - 1; index++) {
      const next = destinationList[index + 1];
      const current = destinationList[index];
      const nearestPOItoMarker = graph.findNearestPOIPoint([next.lat, next.lng]);
      const nearestPOItoUser = graph.findNearestPOIPoint({ lat: current.lat, lng: current.lng }, true);
      if (nearestPOItoMarker && nearestPOItoUser) {
        const middlePath = graph
          .findShortestPath(nearestPOItoUser.id, nearestPOItoMarker.id)
          .map((curr: PoiCoordinates) => [curr.lat, curr.lng] as LatLngExpression);
        const tempPath: LatLngExpression[] = [
          { lat: current.lat, lng: current.lng },
          ...middlePath,
          [next.lat, next.lng],
        ];
        // if(arrIndexPoint.length !== 0)
        //   arrIndexPoint.push(arrIndexPoint[arrIndexPoint.length - 1] + tempPath.length - 1)
        tourPath = [...tourPath, ...tempPath];
        arrIndexPoint.push(tourPath.length-1)
      }
    }
    setArrIndexTourPoint(arrIndexPoint)
    setPathTour(tourPath)
    }
    const getCurrentVisitPoint = useMemo(() => {
      if (!tour || tour.length === 0) return undefined;
      return tour[0];
    },[tour])
    const popVisitedPoint = () =>{
      if (!tour || !arrIndexTourPoint || tour.length === 0 || arrIndexTourPoint.length === 0) return undefined;
    
      if(tour.length > 2){
        setCurrentVisitPoint(tour.slice(1,tour.length)[0])
        setArrIndexTourPoint(arrIndexTourPoint.slice(1,arrIndexTourPoint.length))
        setTour(tour.slice(1,tour.length))
        setPathTour(path?.slice(arrIndexTourPoint.slice(1,arrIndexTourPoint.length)[0],path.length))
      } else if(tour.length == 2){
        setCurrentVisitPoint(tour[1])
        setArrIndexTourPoint([0])
        setTour([tour[1]])
        setPathTour(undefined)
      } else if(tour.length == 1) {
        setCurrentVisitPoint(null)
        setArrIndexTourPoint(undefined)
        setTour(undefined)
      }
    }
    const getCurrentTourPointIDList = useMemo(() => {
      if(tour)
        return tour.map(curr=>curr.tour_point.id)
      return null
    },[tour])

    // effect
    useEffect(()=>{
        const fetchTourPoints = async()=>{
          let data = await tourApi.getTour(TOUR_ID_DEFAULT,selectedLanguageCode)
          data.sort((a,b)=>a.order - b.order)
          if(getCurrentVisitPoint){
            data = data.filter(curr => curr.order >= getCurrentVisitPoint.order)
            setTour(data)
          } else {
            setTour(data)
            setCurrentVisitPoint(data[0])
            drawTour(data)
          }
        }
        fetchTourPoints()
    },[selectedLanguageCode])

    useEffect(()=>{
      const pathToNextVisitPoint = drawPathToNextPointInTour()
      if(pathTour && pathToNextVisitPoint)
        setPath([...pathToNextVisitPoint,...pathTour])
      else if(pathTour == undefined && pathToNextVisitPoint)
        setPath(pathToNextVisitPoint)
      // if(pathTour)
      //   setPath([...pathTour])
    },[pathTour,userLocation])
    useEffect(() => {
        // if not near the visit point
        if(isNear){
          popVisitedPoint()

        }
    }, [isNear]);

    return (
      <MapContainer
        ref={ref}
        center={PAGODA_POSITION as LatLngTuple}
        zoom={18}
        scrollWheelZoom={false}
        style={{ height: "100vh", width: "100vw", zIndex: 0 }}
        maxBounds={PAGODA_BOUNDS}
        zoomAnimation={true}
        fadeAnimation={false}
        bounceAtZoomLimits={false}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          maxZoom={19}
          minZoom={17}
          edgeBufferTiles={1}
          keepBuffer={30}
        />
        {tour?.map((component:PoiApiTour,index) => (
          <Marker
            key={component.tour_point.id}
            position={[component.tour_point.position.lat, component.tour_point.position.lng]}
            icon={L.divIcon({
              className: "",
              html: renderToString(
                !isStartTour?
                <TourPointMarkerBeforeTour _No={component.order.toString()} name={component.tour_point.localizedData.name}/>
                :<CustomMarkerIcon
                  name={component.tour_point.localizedData.name}
                  image={component.tour_point.thumbnail}
                  isClose={index == 0}
                  isInTour={true}
                />
              ),
              iconSize: [34, 34],
              iconAnchor: [22, 30],
            })}
            eventHandlers={{
            //   click: () => handleClickMarker(component),
            }}
          />
        ))}
        {poiData?.map((component) => (
          <Marker
            key={component.id}
            position={[component.position.lat, component.position.lng]}
            icon={L.divIcon({
              className: "",
              html: renderToString(
                !getCurrentTourPointIDList?.includes(component.id) &&
                <CustomMarkerIcon
                  name={component.localizedData.name}
                  image={component.thumbnail}
                  isClose={false}
                  isOpacity = {true}
                />
              ),
              iconSize: [34, 34],
              iconAnchor: [22, 30],
            })}
            eventHandlers={{
            //   click: () => handleClickMarker(component),
            }}
          />
        ))}
        { 
        isStartTour
         ? path?.map(curr=>(<LeadMarker position={curr}  />))
         :<Polyline positions={path ? path : []} color="#ffb700" />
        }

        <UserMarker />
      </MapContainer>
    );
  },
);
export default TourMap;
