import L from "leaflet"
import { LatLngExpression } from "leaflet";
import { FC } from "react";
import { Marker } from "react-leaflet"
import { renderToString } from "react-dom/server";

type TProps = {
    position: LatLngExpression
}
const LeadMarker:FC<TProps> = (props) => {

    return (
        <Marker
        position={props.position}
        icon={L.divIcon({
            className: "",
            html: renderToString(<CustomLeadMarker/>),
            iconSize: [20, 20],
            iconAnchor: [15, 15],
        })}
        />
    )
}
export default LeadMarker

const CustomLeadMarker = ()=>{
    return(
        <div style={{
            width: "15px",
            height: "15px",
            borderRadius: "50%",
            backgroundColor: "#C6E6CD",
            border: "2px solid",
            borderColor: "#4DB658",
        }}></div>
    )
}