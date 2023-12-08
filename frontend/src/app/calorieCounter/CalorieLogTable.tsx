import { useAppSelector } from "@/app/_components/store/hooks";
import { selectCalorieLog, snapNutritionData } from "@/app/_components/store/calorieLogSlice";
import {
    Card,
    CardContent,
    CardHeader, Link,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow, Typography
} from "@mui/material";

import styles from "@/app/page.module.css"
import { CalorieEntryDialog } from "@/app/calorieCounter/CalorieEntryDialog";
import { useState } from "react";
import { base64Thumbnail } from "@/app/_components/util/imageTools";
import NextLink from "next/link";
import { usePathname } from "next/navigation";




export default function CalorieLogTable(){
    const calorieLog = useAppSelector(selectCalorieLog)

    const [open, setOpen] = useState(false);
    const [selectedValue, setSelectedValue] = useState("");
    const [calorieEntry, setCalorieEntry] = useState<snapNutritionData | null>(null)
    const currentPath = usePathname();


    const handleClose = (value: string) => {
        setOpen(false);
        setSelectedValue(value);
    };

    function entryPopup(entry: snapNutritionData) {
        setOpen(true);
        setCalorieEntry(entry)
        console.log(entry)
    }


    const calorieTable = (
        <TableContainer>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Thumbnail</TableCell>
                        <TableCell>Photo Name</TableCell>
                        <TableCell align="right">Calories</TableCell>
                        <TableCell align="right">Total Mass (g)</TableCell>
                        <TableCell align="right">Fat&nbsp;(g)</TableCell>
                        <TableCell align="right">Carbs&nbsp;(g)</TableCell>
                        <TableCell align="right">Protein&nbsp;(g)</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {calorieLog.map((entry: snapNutritionData, idx) => (
                        <TableRow
                            key={idx}
                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                            onClick={() => entryPopup(entry)}
                        >
                            <TableCell component="th" scope="row">
                                {base64Thumbnail(entry.photoBase64)}
                            </TableCell>
                            <TableCell component="th" scope="row">
                                {entry.photoName}
                            </TableCell>
                            <TableCell align="right">{entry.calories}</TableCell>
                            <TableCell align="right">{entry.total_mass_g}</TableCell>
                            <TableCell align="right">{entry.fat_g}</TableCell>
                            <TableCell align="right">{entry.carbs_g}</TableCell>
                            <TableCell align="right">{entry.protein_g}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
    </TableContainer>
    )

    const clickHere = <Link component={NextLink} href={"/calorieCounter"}>Go here to upload something!</Link>
    const alreadyHere = "Use the photo uploader to upload something!"
    const emptyContent = (<Typography>
        You haven&apos;t uploaded any photos yet! {currentPath == "/calorieCounter" ?
        alreadyHere : clickHere}
    </Typography>)

    return (
        <Card className={styles.card}>
            <CalorieEntryDialog selectedValue={selectedValue}
                                open={open}
                                onClose={handleClose}
                                calorieEntry={calorieEntry}/>

            <CardHeader title={"Calorie Log"} titleTypographyProps={{color: "white"}} />
            <CardContent>
                {calorieLog.length == 0 ? emptyContent: calorieTable}
            </CardContent>

        </Card>


    )
}
