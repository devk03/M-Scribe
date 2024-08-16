//Defining a data model for timestamps response
class TimestampsResponse {
    timestamps string @description(#"
        A formatted guide of timestamps and key content points from the lecture transcript.
    "#)
}

//function to extract and format timestamps from transcript to a string
function CreateTimestampGuide(transcript: string) -> TimestampsResponse {
    client GPT4o_mini
    
    prompt #"

    You are a chatbot designed to assist University of Michigan students by extracting important timestamps from lecture transcripts. 
    Create a concise guide that includes timestamps, brief section titles, 
    and a one-sentence summary for each section, using emojis for visual appeal.

    Transcript:
    {{ transcript }}

    {{ ctx.output_format }}
    "#
}