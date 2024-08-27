//Defining a data model for timestamps response
class TimestampsResponse {
    timestamps Timestamp[] @description(#"
        An array of timestamp objects containing detailed information about key points in the lecture.
    "#)
}

class Timestamp {
    time string @description(#"The timestamp in HH:MM:SS format"#)
    title string @description(#"A brief title for the section"#)
    summary string @description(#"A one-sentence summary of the section"#)
    emoji string @description(#"An appropriate emoji for the section"#)
}

//function to extract and format timestamps from transcript to a string
function CreateTimestampGuide(transcript: string) -> TimestampsResponse {
    client GPT4o_mini
    
    prompt #"
    You are a chatbot designed to assist University of Michigan students by extracting important timestamps from lecture transcripts. 
    Create a concise guide that includes timestamps, brief section titles, 
    a one-sentence summary for each section, and an appropriate emoji.

    Transcript:
    {{ transcript }}

    Return the result as an array of Timestamp objects, where each object has the following structure:
    {
        time: "HH:MM:SS",
        title: "Brief section title",
        summary: "One-sentence summary of the section",
        emoji: "Appropriate emoji"
    }
    "#
}