from fastapi import APIRouter, Request
from .utils.rag import get_closest_snippets

router = APIRouter()

@router.post("/query")
async def read_users(request: Request):
    body = await request.json()
    lectureID = body.get("lectureID")
    queryText = body.get("queryText")
    if not lectureID or not queryText:
        return {"error": "lectureID or queryText not found in request body"}
    
    results = get_closest_snippets(queryText, lectureID)
    return results
