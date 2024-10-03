import datetime
import hashlib
import logging
import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from fastapi import Depends
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from database import get_db
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")


# Authentication function
def authenticate_user(db: Session, username: str, password: str):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")

    # Hash the password and compare
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if hashed_password != user.password:
        raise HTTPException(status_code=401, detail="Invalid password")

    return user


# JWT token creation
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# JWT token validation
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            try:
                payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
                # You could validate claims here,
                # e.g., check if 'sub' (username) matches a user in your database
                return credentials
            except jwt.ExpiredSignatureError:
                logger.warning("Token has expired")
                raise HTTPException(status_code=403, detail="Token has expired")
            except jwt.InvalidTokenError:
                logger.warning("Invalid token")
                raise HTTPException(status_code=403, detail="Invalid token")
            except Exception as e:
                logger.error(f"Error decoding token: {e}")
                raise HTTPException(status_code=403, detail="Invalid or expired token")
        else:
            logger.warning("Authorization header is missing")
            raise HTTPException(status_code=403, detail="Authorization header is required")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(JWTBearer()), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=403, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=403, detail="Invalid token")


def require_role(role: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user: User = kwargs.get('user')
            if user is None:
                raise HTTPException(status_code=401, detail="User not authenticated")
            if user.role != role:
                raise HTTPException(status_code=403, detail="Operation not permitted")
            return await func(*args, **kwargs)

        return wrapper

    return decorator
