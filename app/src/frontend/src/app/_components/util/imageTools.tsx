import Image from "next/image";

export function base64Thumbnail(base64Str: string | ArrayBuffer | null, baseWidthValue = 200){
    // blurURL prevents some complaints with re-rendering, I've just put a tiny base64 image as the placeholder
    const blurUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADAAAABAAgMAA" +
        "AAhThzVAAAADFBMVEX///+IiIjDw8PExMTmLg9mAAAAAXRSTlMAQObYZgAAAGpJREFUKJHN0rkNACEMRNEvMgqhJMsJRdAM/bi0DdhjQkO0" +
        "zl7gGckydk8APBiKrnAAAwCbIWhDULuguAQwQ9CGoHZB8S8AZgjaENQuKP4GmJmlwTt5nPaYpiWwVvdw3PPju7GeI42Tnn1cuaO" +
        "hRIkVzr8AAAAASUVORK5CYII="

    const width = `${baseWidthValue}px`
    const height = `${baseWidthValue * .6}px`

    return (
        <div style={{ position: 'relative', width, height }}>
            <Image src={base64Str as string} placeholder={"blur"} blurDataURL={blurUrl} alt={"Upload Image"} sizes={"50px"}
                   fill style={{objectFit: "contain"}} />
        </div>
    )
}