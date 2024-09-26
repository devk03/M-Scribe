from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from routers.rag import ragRoutes
from routers.scraping import scrapingRoutes

# Load environment variables
load_dotenv(find_dotenv())

# Initialize FastAPI app
app = FastAPI()

# Query /token to get the token
tokenBearer = OAuth2PasswordBearer(tokenUrl="token")

# TODO: Change this to a .env variable, and generate a legitimate one (currently testing)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Define authentication classes
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ragRoutes.router)
app.include_router(scrapingRoutes.router)


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Test"}


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # TODO: Authenticate the user with Auth0
    user = None
    # If authentication fails, raise an exception
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Create an access token expiration time
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create the access token
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    # Return the token and its type
    return Token(access_token=access_token, token_type="bearer")


@app.get("/test")
async def test(token: Annotated[str, Depends(tokenBearer)]):
    return {"token": token}
