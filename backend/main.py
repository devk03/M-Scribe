from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
import requests
from routers.scraping import scrapingRoutes
from routers.rag import ragRoutes

load_dotenv(find_dotenv())

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers from various modules
app.include_router(scrapingRoutes.router)
app.include_router(ragRoutes.router)


@app.get("/")
async def root():
    return {"message": "Test"}
