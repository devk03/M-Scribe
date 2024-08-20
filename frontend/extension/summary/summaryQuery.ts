export const summaryQuery = async (lectureID: string, queryText: string) => {
    const settings = {
        method: 'POST',
        body: JSON.stringify({
            CAEN_ID: lectureID,
            queryText: queryText,
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

        return data.response; // I think summary is just the response string
    }
    catch (error) {
        console.error("Error querying FastAPI Backend:", error);
        throw error; // Rethrow the error for the caller to handle
    }    
}