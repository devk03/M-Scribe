export const summaryQuery = async (lectureID: string) => {
    const settings = {
        method: 'POST',
        body: JSON.stringify({
            CAEN_ID: lectureID,
        }),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    };

    try {
        console.log("Querying FastAPI Backend: ", `${process.env.PLASMO_PUBLIC_BACKEND}/summary`);
        const fetchResponse = await fetch(`${process.env.PLASMO_PUBLIC_BACKEND}/summary`, settings);

        const data = await fetchResponse.json();
        console.log("Response from FastAPI Backend:", data);

        return data 
    }
    catch (error) {
        console.error("Error querying FastAPI Backend:", error);
        throw error; // Rethrow the error for the caller to handle
    }    
}