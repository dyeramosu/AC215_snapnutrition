import { useAppSelector } from "@/app/_components/store/hooks";
import { selectCalorieLog } from "@/app/_components/store/calorieLogSlice";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material";
import Image from "next/image";




function base64Thumbnail(base64Str: string | ArrayBuffer | null){
    // blurURL prevents some complaints with re-rendering, I've just put a tiny base64 image as the placeholder
   const blurUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAABAAgMAA" +
       "AAhThzVAAAADFBMVEX///+IiIjDw8PExMTmLg9mAAAAAXRSTlMAQObYZgAAAGpJREFUKJHN0rkNACEMRNEvMgqhJMsJRdAM/bi0DdhjQkO0" +
       "zl7gGckydk8APBiKrnAAAwCbIWhDULuguAQwQ9CGoHZB8S8AZgjaENQuKP4GmJmlwTt5nPaYpiWwVvdw3PPju7GeI42Tnn1cuaO" +
       "hRIkVzr8AAAAASUVORK5CYII="

    return (
        <div style={{ position: 'relative', width: '50px', height: '30px' }}>
            <Image src={base64Str as string} placeholder={"blur"} blurDataURL={blurUrl} alt={"Upload Image"} sizes={"50px"}
                   fill style={{objectFit: "contain"}} />
        </div>
    )
}
export default function CalorieLogTable(){
    const calorieLog = useAppSelector(selectCalorieLog)


    return (
        <TableContainer>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableCell>Thumbnail</TableCell>
                        <TableCell>Photo Name</TableCell>
                        <TableCell align="right">Calories</TableCell>
                        <TableCell align="right">Fat&nbsp;(g)</TableCell>
                        <TableCell align="right">Carbs&nbsp;(g)</TableCell>
                        <TableCell align="right">Protein&nbsp;(g)</TableCell>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {calorieLog.map((entry, idx) => (
                        <TableRow
                            key={idx}
                            sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                        >
                            <TableCell component="th" scope="row">
                                {base64Thumbnail(entry.photoBase64)}
                            </TableCell>
                            <TableCell component="th" scope="row">
                                {entry.photoName}
                            </TableCell>
                            <TableCell align="right">{entry.total_calories}</TableCell>
                            <TableCell align="right">{entry.total_fat}</TableCell>
                            <TableCell align="right">{entry.total_carb}</TableCell>
                            <TableCell align="right">{entry.total_protein}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>

            </Table>
        </TableContainer>

    )
}
