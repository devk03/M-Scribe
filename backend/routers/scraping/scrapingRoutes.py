from fastapi import APIRouter, Request
from .utils.parsing import removeTimestamps, parseTranscript, printToFile
from ..rag.utils.rag import process_and_post_text
import requests

router = APIRouter()


def add_delimiters(text, chunk_size=500, delimiter="#####"):
    delimited_text = ""
    for i, char in enumerate(text):
        delimited_text += char
        if (i + 1) % chunk_size == 0 and i < len(text) - 1:
            delimited_text += delimiter
    return delimited_text


@router.post("/lecture")
async def fetch_lecture(request: Request):
    # Parse the JSON body
    body = await request.json()

    # Get the specific PHPSESSID from the JSON body
    PHPSESSID = body.get("PHPSESSID")
    CAEN = body.get("CAEN_ID")
    if not PHPSESSID:
        return {"error": "PHPSESSID not found in request body"}
    if not CAEN:
        return {"error": "CAEN_ID not found in request body"}

    url = f"https://leccap.engin.umich.edu/leccap/player/api/webvtt/?rk={CAEN}"
    # Use the extracted PHPSESSID to make the request
    response = requests.get(url, cookies={"PHPSESSID": PHPSESSID})

    # Parse the content of all timestamps from the response
    print(">>> Removing timestamps")
    rawTranscript = removeTimestamps(response.content.decode("utf-8"))
    print(">>> Parsing transcript")
    parsedTranscript = parseTranscript(rawTranscript)
    print(">>> Adding delimiters")
    delimitedTranscript = add_delimiters(parsedTranscript)
    print(">>> Posting vectors to Pinecone")
    process_and_post_text(delimitedTranscript, CAEN)

    return {"content": delimitedTranscript}
