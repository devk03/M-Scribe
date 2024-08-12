import re
import openai
import os

from openai import OpenAI

openai.api_key = os.environ.get("AJ KEY")

def add_delimiters(text, chunk_size=300, delimiter="#####"):
    print("Adding delimiters to text")
    delimited_text = ""
    for i, char in enumerate(text):
        delimited_text += char
        if (i + 1) % chunk_size == 0 and i < len(text) - 1:
            delimited_text += delimiter
    return delimited_text

#-----------------------------------------------------------------------------------------

def extractTimestamps(transcript):
    # match timestamps with milliseconds
    pattern = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3})\s-->\s(\d{2}:\d{2}:\d{2}\.\d{3})\n(.+?)\n", re.DOTALL)
    segments = pattern.findall(transcript)
    return [{'start': start, 'end': end, 'text': text.strip()} for start, end, text in segments]

def process_segments(segments):
    transcript_text = "\n".join([segment['text'] for segment in segments])

    prompt = (
        "Transform the following lecture transcript into a concise timestamp guide for a student chatbot. "
        "Include brief section titles, timestamps, key takeaways, and use emojis for visual appeal. "
        "Format the output for easy reading.\n\n"
        f"{transcript_text}"
    )

    client = OpenAI(api_key=openai.api_key)
    output = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.7,
    )

    study_guide = output.choices[0].message.content
    return study_guide

#-----------------------------------------------------------------------------------------

def removeTimestamps(transcript):
    print(">>> Removing Timestamps\n")
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