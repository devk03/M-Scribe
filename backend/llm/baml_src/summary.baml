// Defining a data model for the summary response
class SummaryResponse {
    summary string @description(#"
        A concise summary of the lecture content.
    "#)
    notes string[] @description(#"
        Important notes highlighting key concepts from the lecture.
    "#)
    reviewQuestions string[] @description(#"
        Review questions the student should be able to answer after watching the lecture.
    "#)
}


// Creating a function to generate the summary response
functions StructureSummary(text: string) -> SummaryResponse {
    client GPT4o_mini

    prompt #"
    You are an AI assistant that that is meant to help college students review their class content. 
    Your task is to create a study guide of the lecture.
    Please provide the following:

    1. A 4-5 sentence summary of the lecture.
    2. A list of 6-8 key notes from the lecture.
    3. A list of 6-8 review questions the student should be able to answer watching the lecture.
    
    Text:
    {{text}}

    Return the result in the format of SummaryResponse, with the summary, notes, and reviewQuestions fields filled. 
    "#
}