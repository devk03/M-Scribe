// postLecture.ts - Purpose: Fetch data from FastAPI Public Backend
export const postLecture = async (CAEN_ID: string, PHPSESSID: string) => {
    
    const settings = {
        method: 'POST',
        body: JSON.stringify({
            "CAEN_ID": CAEN_ID,
            "PHPSESSID": PHPSESSID,
        }),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    };

    try {
        console.log("Fetching data from FastAPI Public Backend: ", process.env.PLASMO_PUBLIC_BACKEND);
        const fetchResponse = await fetch(`${process.env.PLASMO_PUBLIC_BACKEND}/lecture`, settings);
        const data = await fetchResponse.json();
        return data;
    } catch (error) {
        console.log(error);
        return error;
    }    

}