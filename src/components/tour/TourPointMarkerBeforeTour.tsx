import { TOUR_POINT_MARKER, TOUR_POINT_MARKER_LABEL } from "@/constants/marker"
import { FC } from "react"

type TTourPointMaker = {
    _No: string
    name: string
}
const TourPointMarkerBeforeTour:FC<TTourPointMaker> = (props) => {
  return(
    <div
      style={{
        width: "30px",
        height: "30px",
        borderRadius: "50%",
        border: "2px solid",
        borderColor: TOUR_POINT_MARKER.border,
        display: "flex",
        background: TOUR_POINT_MARKER.background,
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
        position: "relative",
        color: TOUR_POINT_MARKER.text,
        fontSize: "16px",
        fontWeight: "bold"
      }}
    >
      {props._No}
      <div
      style={{
        position: "absolute",
        bottom: "-30px",
        width: 140,
        padding: "1px 10px 0px 10px",
        textAlign: "center",
        maxWidth: 140,
        height: 20,
        border: "1px solid",
        borderRadius: 10,
        borderColor: TOUR_POINT_MARKER_LABEL.borderColor,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
        background: TOUR_POINT_MARKER_LABEL.background,
        color: "black",
        fontSize: 12,
        fontWeight: "normal",
        // boxShadow: "0px 0px 12px -5px rgba(0,0,0,0.89)",
      }}
    >
      {props.name}
    </div>
    </div>
  )
}

export default TourPointMarkerBeforeTour