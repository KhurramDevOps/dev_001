from datetime import datetime, timedelta, timezone
from typing import Any
from jose import jwt, JWTError
import hashlib
from passlib.context import CryptContext

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.modules.users.schemas import TokenData # Need this for type hinting


# Use bcrypt_sha256 so long/unicode passwords are pre-hashed with SHA256 automatically.
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")

# OAuth2 scheme for dependency injection in controllers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

# --- Password Hashing/Verification ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --- JWT Token Handling ---

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception) -> TokenData:
    """Verifies a JWT token and returns the payload data."""
    try:
        # Decode the token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Extract user ID (subject)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Return the data schema
        token_data = TokenData(user_id=int(user_id))
    
    except JWTError:
        raise credentials_exception
        
    return token_data

# --- Dependency for Protected Endpoints ---

def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """
    Dependency that extracts and verifies the user ID from the JWT.
    Used in protected routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # The verify_token function raises credentials_exception if invalid
    token_data = verify_token(token, credentials_exception)
    return token_data.user_id # Returns the user's ID