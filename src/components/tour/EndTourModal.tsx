import { FC } from "react"
import { Dialog, DialogContent2 } from "../ui/dialog"
import { Button } from "../ui/button"
import useTourStore from "@/store/useTourStore"
import { EXPLORE_WAY } from "@/constants/tour"

type TProp = {
    visible: boolean,
}
const EndTourModal:FC<TProp> = (props) => {
    const {setStartTour, setTypeTour} = useTourStore(state=>state)
    const handleClick = () => {
        setStartTour(false)
        setTypeTour(EXPLORE_WAY.FREE)
    }
    return(
        <Dialog open={props.visible}>
            <DialogContent2 className="flex flex-col justify-center gap-4">
                <h1 className="text-center text-2xl mb-0">Cảm ơn quý khách</h1>
                <p className="text-center mb-3">Quý khách đã đi hết tour tham quan</p>
                <Button
                    variant="primary"
                    className="w-full py-4"
                    onClick={handleClick}
                >
                    Thoát tour
              </Button>
            </DialogContent2>
        </Dialog>
    )
}
export default EndTourModal