import re


def removeTimestamps(transcript):
    # Define the regex pattern to match timestamps
    pattern = r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n"
    # Add pattern for the WEBVTT and possible leading/trailing spaces
    pattern_full = (
        r"WEBVTT\n\n|\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}\n|\n{2,}"
    )

    # Remove the timestamps using the regex pattern
    cleaned_transcript = re.sub(pattern_full, "", transcript)

    # Replace newlines with spaces
    cleaned_transcript = cleaned_transcript.replace("\n", " ")

    return cleaned_transcript.strip()


def parseTranscript(transcript, chunk_size=250):
    """
    Parses the transcript into list/chunks of N words
    """
    # Split the transcript into words
    words = transcript.split()

    # Initialize variables
    chunks = []
    current_chunk = []

    # Iterate over the words and create chunks
    for word in words:
        current_chunk.append(word)
        if len(current_chunk) >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

    # Add the last chunk if it contains any words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return "#####".join(chunks)

def printToFile(obj, filename='output.txt', mode='a'):
    """
    Prints the given object to a file.
    
    :param obj: The object to print (can be any type)
    :param filename: The name of the file to write to (default: 'output.txt')
    :param mode: The file opening mode (default: 'a' for append)
    """
    with open(filename, mode) as f:
        print(obj, file=f)