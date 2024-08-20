from fastapi import APIRouter, Request
from .utils.rag import get_closest_snippets, create_excerpts, create_summary
from scraping.utils.parsing import removeTimestamps, parseTranscript
from llm.baml_client.sync_client import b as BAML_CLIENT
from llm.baml_client.types import QueryResponse
import requests

router = APIRouter()


@router.post("/query")
async def read_users(request: Request):
    body = await request.json()
    CAEN_ID = body.get("CAEN_ID")
    queryText = body.get("queryText")
    if not CAEN_ID or not queryText:
        return {"error": "lectureID or queryText not found in request body"}

    pinecone_response = get_closest_snippets(queryText, CAEN_ID)
    excerpts = create_excerpts(pinecone_response)
    bamlResponse = BAML_CLIENT.ExtractResponse(excerpts, queryText)
    return bamlResponse

@router.post("/summary")
async def fetch_lecture(request: Request):
   
    body = await request.json()

    PHPSESSID = body.get("PHPSESSID")
    CAEN = body.get("CAEN")

    if not PHPSESSID:
        return {"error": "PHPSESSID not found in request body"}

    url = f"https://leccap.engin.umich.edu/leccap/player/api/webvtt/?rk={CAEN}"

    # Use the extracted PHPSESSID to make the request
    response = requests.get(url, cookies={"PHPSESSID": PHPSESSID})
    rawTranscript = removeTimestamps(response.content.decode("utf-8"))
    parsedTranscript = parseTranscript(rawTranscript)

    #using GPT API to create the summary
    secondSummary = create_summary(parsedTranscript)

    return secondSummary