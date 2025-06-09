import { TMarkerStyle } from "@/types/marker"

export const TOUR_POINT_MARKER = {
    border: "#FFFFFF",
    background: "#FFA040",
    text: "#FFFFFF"
}
export const TOUR_POINT_MARKER_LABEL = {
    background: "white",
    borderColor: "#34A538"
}
export const enum STATUS_MARKER {
    ACTIVATE = 1,
    NORMAL_OUT_TOUR = 2,
    NORMAL_IN_TOUR = 3
}
export const MARKER_ICON_STYLE:Record<STATUS_MARKER,TMarkerStyle> = {
    [STATUS_MARKER.ACTIVATE] : {
        width: "56px",
        height: "56px",
        colorLocationIcon: "#3BAA4E",
        strokeLocationIcon: "#3BAA4E",
        backgroundText: "#34A538"
    },
    [STATUS_MARKER.NORMAL_IN_TOUR] : {
        width: "46px",
        height: "46px",
        colorLocationIcon: "#C8C8C8",
        strokeLocationIcon: "#C8C8C8"
    },
    [STATUS_MARKER.NORMAL_OUT_TOUR] : {
        width: "46px",
        height: "46px",
        colorLocationIcon: "#FFFFFF",
        strokeLocationIcon: "#3BAA4E"
    }
}
