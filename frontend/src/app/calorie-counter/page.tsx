'use client'
import { Button, Card, CardHeader, styled } from "@mui/material";
import { useRef } from "react";
import { CloudUpload } from "@mui/icons-material";
import { usePostFoodPicMutation } from "@/app/_components/store/snapNutritionApiSlice";
import { readFile } from "@/app/_components/util/fileHandling";
import CalorieLogTable from "@/app/calorie-counter/CalorieLogTable";
import { useAppDispatch } from "@/app/_components/store/hooks";
import { addCalorieEntry } from "@/app/_components/store/calorieLogSlice";
import styles from "@/app/page.module.css"
import Dropzone from "react-dropzone";
import FastfoodIcon from '@mui/icons-material/Fastfood';
//import { padding } from "@mui/system";


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

const DropZoneDiv = styled('div')({
    border: "2px dashed darkgrey",
    backgroundColor: "lightblue",
    minHeight: "200px",
    justifyContent: "center",
    display: "flex",
    alignItems: "center",
    borderRadius: "25px"
})

export default function CalorieCounter() {

    const [postFoodPic] = usePostFoodPicMutation()
    const dispatch = useAppDispatch();
    const fileInput = useRef<HTMLInputElement>(null);



    async function handleUpload(fileList: File[] | FileList | null) {
        console.log(fileList)
        for (let file of fileList!) {
            const photoName = file.name
            const photoURL = URL.createObjectURL(file);

            const formData = new FormData()
            formData.append("file", file)
            const result = await postFoodPic(formData).unwrap()
            const calorieEntry = {
                photoBase64: photoURL,
                photoName,
                ...result
            }
            dispatch(addCalorieEntry(calorieEntry))

        }
        fileInput.current!.value = "";

    }

    const uploadButton = (
        <Button sx={{padding: "15px", maxWidth: "200px"}} component="label" variant="contained" startIcon={<CloudUpload/>}>
            Upload Photo
            <VisuallyHiddenInput type="file" accept={"image/png, image/jpeg"} ref={fileInput}
                                 onInput={e => handleUpload(e.currentTarget.files)}/>
        </Button>
    )


    const photoDropzone = (
        <Dropzone onDrop={(acceptedFiles: File[]) => handleUpload(acceptedFiles)} accept={{'image/*': ['.jpeg', '.png']}}>
            {({getRootProps, getInputProps}) => (
                <section>
                    <DropZoneDiv {...getRootProps()}>
                        <input {...getInputProps()} />

                        <div style={{position: 'relative', width: '300px', height: '100px', alignItems: "center", display: "flex", justifyContent: "center"}}>
                            <p><b>Drag or click here to upload photos</b></p>
                            <FastfoodIcon style={{position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', color: "rgb(100 100 100 / 0.15)"}} />
                        </div>
                    </DropZoneDiv>
                </section>
            )}
        </Dropzone>
    )

    return (
        <>
            <div style={{padding: "15px"}}>
                <Card className={styles.card}>
                    <CardHeader title={"Food Image Upload"} titleTypographyProps={{color: "white"}} />
                    <div style={{padding: "25px"}}>
                        {photoDropzone}
                    </div>
                    <div style={{display: "flex", justifyContent: "center", padding: "20px"}}>
                        {uploadButton}
                    </div>
                </Card>
            </div>
            <CalorieLogTable/>
        </>
    )
}
