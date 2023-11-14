export async function readFile(file: File): Promise<string | ArrayBuffer | null>{
    const reader = new FileReader()

    return new Promise((resolve, reject) => {
        reader.onerror = ()  => {
            reader.abort();
            reject("An error occurred when reading the file")
        }
        reader.onload = () => {
            resolve(reader.result)
        }
        reader.readAsDataURL(file)

    })
}
