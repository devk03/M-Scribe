from fastapi import APIRouter, Request
from .utils.rag import get_closest_snippets, create_excerpts
from llm.baml_client.sync_client import b as BAML_CLIENT
from llm.baml_client.types import QueryResponse

router = APIRouter()


@router.post("/query")
async def read_users(request: Request):
    body = await request.json()
    CAEN_ID = body.get("CAEN_ID")
    queryText = body.get("queryText")
    chatContext = body.get("chatContext")

    if chatContext:
        chatContext = str(chatContext[-6:])
    if not CAEN_ID or not queryText:
        return {"error": "lectureID or queryText not found in request body"}

    pinecone_response = get_closest_snippets(queryText, CAEN_ID)        
    excerpts = create_excerpts(pinecone_response)

    if chatContext: # There are previous chat messages present
        bamlResponse = BAML_CLIENT.ExtractResponseWithContext(excerpts, queryText, chatContext)
    else:
        bamlResponse = BAML_CLIENT.ExtractResponse(excerpts, queryText)

    return bamlResponse
