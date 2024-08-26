import type { SummaryResponse } from "./type";

export const summaryQuery = async (lectureID: string, PHP: string) : Promise<SummaryResponse> => {
    const settings = {
        method: 'POST',
        body: JSON.stringify({
            CAEN_ID: lectureID,
            PHPSESSID: PHP
        }),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    };


    try {
        console.log("Request body:", settings.body);
        console.log("Querying FastAPI Backend: ", `${process.env.PLASMO_PUBLIC_BACKEND}/summary`);
        const fetchResponse = await fetch(`${process.env.PLASMO_PUBLIC_BACKEND}/summary`, settings);
        console.log("Request body:", settings.body);

        const data = await fetchResponse.json();
        console.log("Response from FastAPI Backend:", data);

        return data as SummaryResponse
    }
    catch (error) {
        console.error("Error querying FastAPI Backend:", error);
        throw error; // Rethrow the error for the caller to handle
    }    
}