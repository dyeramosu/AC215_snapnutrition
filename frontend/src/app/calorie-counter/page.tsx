'use client'
import { Button, styled } from "@mui/material";
import { useRef } from "react";
import { CloudUpload } from "@mui/icons-material";
import { usePostFoodPicMutation } from "@/app/_components/store/snapNutritionApiSlice";
import { readFile } from "@/app/_components/util/fileHandling";
import CalorieLogTable from "@/app/calorie-counter/CalorieLogTable";
import { useAppDispatch } from "@/app/_components/store/hooks";
import { addCalorieEntry } from "@/app/_components/store/calorieLogSlice";


// This is ripped from MUI's button page, just enables you to have a button that acts as an input.
const VisuallyHiddenInput = styled('input')({
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
});

export default function CalorieCounter() {

    const [postFoodPic] = usePostFoodPicMutation()
    const dispatch = useAppDispatch();
    const fileInput = useRef<HTMLInputElement>(null);

    async function handleUpload() {
        const fileList = fileInput.current?.files
        for (let file of fileList!) {
            const photoName = file.name
            const photoBase64 = await readFile(file)
            const result = await postFoodPic({photoBase64, photoName}).unwrap()
            const calorieEntry = {
                photoBase64,
                ...result
            }
            dispatch(addCalorieEntry(calorieEntry))

        }
        fileInput.current!.value = "";
    }

    return (
        <>
            <div style={{padding: "15px"}}>
                <Button sx={{padding: "15px"}} component="label" variant="contained" startIcon={<CloudUpload/>}>
                    Upload file
                    <VisuallyHiddenInput type="file" accept={"image/png, image/jpeg"} ref={fileInput}
                                         onInput={handleUpload}/>
                </Button>
            </div>
            <CalorieLogTable/>
        </>
    )
}
