import { Dialog, DialogTitle } from "@mui/material";
import { base64Thumbnail } from "@/app/_components/util/imageTools";
import { snapNutritionData } from "@/app/_components/store/calorieLogSlice";

export interface SimpleDialogProps {
    open: boolean;
    selectedValue: string;
    onClose: (value: string) => void;
    calorieEntry: snapNutritionData | null
}

export function CalorieEntryDialog(props: SimpleDialogProps) {
    const { onClose, selectedValue, open } = props;

    const handleClose = () => {
        onClose(selectedValue);
    };

    const handleListItemClick = (value: string) => {
        onClose(value);
    };

    const thumbnail = (
            <div style={{padding: "25px"}}>
                {props.calorieEntry != null && base64Thumbnail(props.calorieEntry.photoBase64, 500)}
            </div>
        )


    return (
        <Dialog onClose={handleClose} open={open}>
            {/*<DialogTitle>Entry Info</DialogTitle>*/}
            {thumbnail}

        </Dialog>
    );
}