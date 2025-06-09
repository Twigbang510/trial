import { EXPLORE_WAY } from "@/constants/tour"
import { calculateDistance } from "@/lib/geo"
import useMapStore from "@/store/useMapStore"
import useTourStore from "@/store/useTourStore"
import { useMemo } from "react"

const useTourPoint = () => {
    const {currentVisitPoint: currentVisitPointHook,typeTour} = useTourStore(state=>state)
    const {userLocation}  = useMapStore()
    const isNear = useMemo(() => {
        if (!userLocation || typeTour !== EXPLORE_WAY.TOUR || !currentVisitPointHook) return false
        const distance = calculateDistance(
        [userLocation.lat, userLocation.lng],
        [currentVisitPointHook.tour_point.position.lat, currentVisitPointHook.tour_point.position.lng]
        )
        return distance <= currentVisitPointHook.tour_point.range
    }, [userLocation, currentVisitPointHook])
    return {isNear,currentVisitPointHook}
}
export default useTourPoint