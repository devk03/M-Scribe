//timestampsQuery.ts - Purpose: Query the FastAPI backend for lecture timestamps

export const timestampsQuery = async (lectureID: string, PHPSESSID: string) => {
    const settings = {
        method: 'POST',
        body: JSON.stringify({
            CAEN_ID: lectureID,
            PHPSESSID: PHPSESSID,
        }),
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        }
    };

    try {
        console.log("Querying FastAPI Backend: ", `${process.env.PLASMO_PUBLIC_BACKEND}/timestamps`);
        const fetchResponse = await fetch(`${process.env.PLASMO_PUBLIC_BACKEND}/timestamps`, settings);

        const data = await fetchResponse.json();
        console.log("Response from FastAPI Backend:", data);

        return data.timestamps;

    } catch (error) {
        console.error("Error querying FastAPI Backend:", error);
        throw error; // Rethrow the error for the caller to handle
    }
}