import requests

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from .utils.parsing import removeTimestamps, parseTranscript, extractTimestamps, add_delimiters, process_segments
from ..rag.utils.rag import process_and_post_text

router = APIRouter()

@router.post("/lecture")
async def fetch_lecture(request: Request):
    # Parse the JSON body
    body = await request.json()

    # Get the specific PHPSESSID from the JSON body
    PHPSESSID = body.get("PHPSESSID")
    CAEN = body.get("CAEN")

    if not PHPSESSID:
        return {"error": "PHPSESSID not found in request body"}

    url = f"https://leccap.engin.umich.edu/leccap/player/api/webvtt/?rk={CAEN}"
    # Use the extracted PHPSESSID to make the request
    response = requests.get(url, cookies={"PHPSESSID": PHPSESSID})

    # Parse the content of all timestamps from the response
    rawTranscript = removeTimestamps(response.content.decode("utf-8"))
    parsedTranscript = parseTranscript(rawTranscript)
    delimitedTranscript = add_delimiters(parsedTranscript)
    process_and_post_text(delimitedTranscript, CAEN)

    return {"content": delimitedTranscript}

@router.post("/timestamps", response_model=str)
async def get_timestamps(request: Request):
    body = await request.json()
    PHPSESSID = body.get("PHPSESSID")
    CAEN = body.get("CAEN")

    if not PHPSESSID:
        return {"error": "PHPSESSID not found in request body"}

    url = f"https://leccap.engin.umich.edu/leccap/player/api/webvtt/?rk={CAEN}"
    # Use the extracted PHPSESSID to make the request
    response = requests.get(url, cookies={"PHPSESSID": PHPSESSID})

    rawTranscript = response.content.decode("utf-8") #extracting transcript
    segments = extractTimestamps(rawTranscript) #extracting timestamps from transcript

    #just a check to see if timestamps were created
    #print("Timestamps:", segments)

    timestampsGuide = process_segments(segments) #using gpt to create study guide

    return JSONResponse(content=timestampsGuide)