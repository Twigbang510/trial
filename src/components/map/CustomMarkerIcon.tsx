import { MARKER_ICON_STYLE, STATUS_MARKER } from "@/constants/marker";
import { TMarkerStyle } from "@/types/marker";

export const CustomMarkerIcon = ({
  name,
  image,
  isClose,
  isInTour = false,
  isOpacity = false,
}: {
  name: string;
  image: string;
  isClose: boolean;
  isInTour?: boolean;
  isOpacity?: boolean;
}) => {
  let style:TMarkerStyle = MARKER_ICON_STYLE[STATUS_MARKER.NORMAL_OUT_TOUR]
  if(isInTour && isClose){
    style = MARKER_ICON_STYLE[STATUS_MARKER.ACTIVATE]
  } else if(isInTour && !isClose){
    style = MARKER_ICON_STYLE[STATUS_MARKER.NORMAL_IN_TOUR]
  }
  return (<div
    style={{
      width: style.width,
      height: style.height,
      // borderRadius: "50%",
      // border: "2px solid",
      // borderColor: "red",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      // boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
      position: "relative",
      opacity: isOpacity ? 0.3 : 1
    }}
  >
    <svg width="31" height="38" viewBox="0 0 31 38" fill="none" xmlns="http://www.w3.org/2000/svg" style={{position:"absolute",zIndex:1}}>
      <path d="M15.0625 1C22.8302 1 29.125 7.3992 29.125 15.2393C29.125 18.7819 27.8476 22.1418 25.5156 24.7617V24.7627L15.8096 35.665L15.0625 36.5039L14.3154 35.665L4.61035 24.7617C2.27697 22.1411 1 18.7811 1 15.2383C1.00007 7.39889 7.29487 1 15.0625 1Z" fill={style.colorLocationIcon} stroke={style.strokeLocationIcon} strokeWidth={2}/>
    </svg>

    <img
      src={image}
      alt="POI"
      style={{
        width: "43%",
        height: "43%",
        objectFit: "contain",
        borderRadius: "50%",
        position: "absolute",
        zIndex: 2,
        top: "20%",
        left: "28%",
      }}
    />
    <div
      style={{
        position: "absolute",
        bottom: "-30px",
        width: 140,
        padding: "1px 10px 0px 10px",
        textAlign: "center",
        maxWidth: 140,
        height: 20,
        borderRadius: 10,
        overflow: "hidden",
        textOverflow: "ellipsis",
        whiteSpace: "nowrap",
        background: style.backgroundText ? style.backgroundText : "#9AA39B",
        color: "white",
        fontSize: 12,

        boxShadow: "0px 0px 12px -5px rgba(0,0,0,0.89)",
      }}
    >
      {name}
    </div>
  </div>
)};

//const MARKER_COLOR = "#30D158";
//
//export const CustomMarkerIcon = ({
//  image,
//  isClose,
//}: {
//  image: string;
//  isClose: boolean;
//}) => (
//  <div
//    style={{
//      position: "relative",
//      width: "50px",
//      height: "90px",
//      display: "flex",
//      alignItems: "center",
//      justifyContent: "center",
//    }}
//  >
//    <div
//      style={{
//        width: "50px",
//        height: "50px",
//        borderRadius: "50%",
//        border: "3px solid",
//        borderColor: MARKER_COLOR,
//        backgroundColor: isClose ? MARKER_COLOR : "white",
//        display: "flex",
//        alignItems: "center",
//        justifyContent: "center",
//        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
//      }}
//    >
//      <img
//        src={image}
//        alt="POI"
//        style={{
//          width: "34px",
//          height: "34px",
//          objectFit: "cover",
//          borderRadius: "50%",
//        }}
//      />
//    </div>
//
//    {/* Triangle pointer */}
//    <div
//      style={{
//        position: "absolute",
//        bottom: 0,
//        left: "50%",
//        transform: "translateX(-50%)",
//        width: 28,
//        height: 0,
//        borderLeft: "7px solid transparent",
//        borderRight: "7px solid transparent",
//        borderTop: "10px solid",
//        borderTopColor: MARKER_COLOR,
//      }}
//    />
//  </div>
//);
