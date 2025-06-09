import { TOUR_TAG } from "@/constants/tag";
import {FC} from "react";

const Tag:FC<{text:string,type:string}> = (props) => {
  const style = TOUR_TAG[props.type] + " w-fit py-2 px-4 rounded-xl"
  return ( 
    <div className="w-fit flex justify-center">
      <div className={style}>{props.text}</div>
    </div>
   );
}
 
export default Tag;