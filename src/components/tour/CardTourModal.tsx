import { FC } from "react"
import { Button } from "../ui/button"
import Tag from "../ui/tag"
import { Dialog } from "@radix-ui/react-dialog"
import { DialogContent2 } from "../ui/dialog"
type TCardTour = {
    onClickBtnStart: ()=>void
    visible: boolean
}
const CardTourModal:FC<TCardTour> = (props) => {
    return(
        <Dialog open={props.visible}>
            <DialogContent2 className="top-[38%]">
                <div className="w-full p-1">
                    <div className="flex gap-3 mb-3">
                        <div className="grow">
                            <h1 className="text-xl">Tour mặc định</h1>
                            <div className="flex gap-3 text-[14px] text-[#8695AA]">
                                <span>10 điểm thu hút</span>
                                <span>1h</span>
                                <span>2.1km</span>
                            </div>
                        </div>
                        <Button className="" title="" onClick={props.onClickBtnStart}>Start Tour</Button>
                    </div>
                    <div className="flex justify-start gap-4 text-[10px]">
                        <Tag text="Dễ đi" type="infor"/>
                        <Tag text="Khám phá" type="infor"/>
                        <Tag text="Người lớn tuổi" type="infor"/>
                    </div>
                </div>
            </DialogContent2>
        </Dialog>
    )
}
export default CardTourModal