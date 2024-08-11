from fastapi import APIRouter, Request
from .utils.parsing import removeTimestamps, parseTranscript, extractTimestamps, add_delimiters
from ..rag.utils.rag import process_and_post_text

from typing import List
from pydantic import BaseModel

import requests

router = APIRouter()

class TranscriptSegment(BaseModel):
    start: str
    end: str
    text: str


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

@router.post("/timestamps", response_model=List[TranscriptSegment])
async def get_timestamps(request: Request):
    body = await request.json()
    PHPSESSID = body.get("PHPSESSID")
    CAEN = body.get("CAEN")

    if not PHPSESSID:
        return {"error": "PHPSESSID not found in request body"}

    url = f"https://leccap.engin.umich.edu/leccap/player/api/webvtt/?rk={CAEN}"
    # Use the extracted PHPSESSID to make the request
    response = requests.get(url, cookies={"PHPSESSID": PHPSESSID})

    transcript = removeTimestamps(response.content.decode("utf-8"))
    segments = extractTimestamps(transcript)

    processed_segments = []
    for segment in segments:
        processed_segments.append({
            "start": segment['start'],
            "end": segment['end'],
            "text": segment['text'],
        })

    return processed_segments