# Import datetime related classes for handling dates and times
from datetime import datetime, timedelta, timezone

# Import typing utilities for type hinting
from typing import Annotated, Union

# Import the JWT (JSON Web Token) library for token handling
import jwt

# Import FastAPI and related utilities
from fastapi import Depends, FastAPI, HTTPException, status

# Import OAuth2 password utilities from FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Import JWT's InvalidTokenError for exception handling
from jwt.exceptions import InvalidTokenError

# Import CryptContext for password hashing
from passlib.context import CryptContext

# Import BaseModel from pydantic for data validation
from pydantic import BaseModel

# Define a secret key for JWT encoding/decoding (in a real app, this should be kept secret)
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# Define the algorithm used for JWT
ALGORITHM = "HS256"
# Define the expiration time for access tokens in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create a fake user database (in a real app, this would be a real database)
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


# Define a Pydantic model for the Token response
class Token(BaseModel):
    # Field for the access token string
    access_token: str
    # Field for the token type (e.g., "bearer")
    token_type: str


# Define a Pydantic model for the data stored in a token
class TokenData(BaseModel):
    # Optional username field
    username: Union[str, None] = None


# Define a Pydantic model for User data
class User(BaseModel):
    # Required username field
    username: str
    # Optional email field
    email: Union[str, None] = None
    # Optional full name field
    full_name: Union[str, None] = None
    # Optional disabled status field
    disabled: Union[bool, None] = None


# Define a Pydantic model for User data stored in the database, inheriting from User
class UserInDB(User):
    # Additional field for the hashed password
    hashed_password: str


# Create a CryptContext instance for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create an OAuth2PasswordBearer instance for token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a FastAPI application instance
app = FastAPI()


# Function to verify a password against its hash
def verify_password(plain_password, hashed_password):
    # Use pwd_context to verify the password
    return pwd_context.verify(plain_password, hashed_password)


# Function to hash a password
def get_password_hash(password):
    # Use pwd_context to hash the password
    return pwd_context.hash(password)


# Function to get a user from the database
def get_user(db, username: str):
    # Check if the username exists in the database
    if username in db:
        # If it exists, get the user dictionary
        user_dict = db[username]
        # Return a UserInDB instance created from the user dictionary
        return UserInDB(**user_dict)


# Function to authenticate a user
def authenticate_user(fake_db, username: str, password: str):
    # Get the user from the database
    user = get_user(fake_db, username)
    # If user doesn't exist, return False
    if not user:
        return False
    # If password doesn't match, return False
    if not verify_password(password, user.hashed_password):
        return False
    # If both checks pass, return the user
    return user


# Function to create an access token
def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    # Create a copy of the input data
    to_encode = data.copy()
    # If an expiration delta is provided, use it; otherwise, default to 15 minutes
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    # Add the expiration time to the token data
    to_encode.update({"exp": expire})
    # Encode the data into a JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # Return the encoded JWT
    return encoded_jwt


# Dependency function to get the current user from a token
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    # Create an exception for invalid credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Attempt to decode the JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Extract the username from the decoded payload
        username: str = payload.get("sub")
        # If no username is found, raise an exception
        if username is None:
            raise credentials_exception
        # Create a TokenData instance with the username
        token_data = TokenData(username=username)
    # If the token is invalid, raise an exception
    except InvalidTokenError:
        raise credentials_exception
    # Get the user from the database
    user = get_user(fake_users_db, username=token_data.username)
    # If the user doesn't exist, raise an exception
    if user is None:
        raise credentials_exception
    # Return the user
    return user


# Dependency function to get the current active user
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    # If the user is disabled, raise an exception
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    # Otherwise, return the user
    return current_user


# Route for user login and token creation
@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    # Authenticate the user
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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


# Route to get information about the current user
@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # Return the current user's information
    return current_user


# Route to get items owned by the current user
@app.get("/users/me/items/")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # Return a list containing a dummy item owned by the current user
    return [{"item_id": "Foo", "owner": current_user.username}]

########################################################

"""Shrey's code"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import requests
from config import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def verify_google_token(token: str):
    response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={token}")
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
    token_info = response.json()
    return token_info

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

@app.post("/signin")
async def signin(payload: AuthRequest):
    response = requests.get(
        url=f'https://{settings.REACT_APP_AUTH0_DOMAIN}/userinfo',
        headers={'Authorization': f'Bearer {payload.auth_token}'},
        timeout=5
    )
    response.raise_for_status()
    data = response.json()
    print(data)