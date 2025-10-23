from pydantic import BaseModel, EmailStr

# Base schema for data shared between input and output
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    
    # Configure Pydantic to accept SQLAlchemy ORM models
    # This addresses the UserWarning about 'orm_mode' being renamed
    class Config:
        from_attributes = True

# Schema for creating a new user (requires password)
class UserCreate(UserBase):
    password: str

# Schema for logging in an existing user (only needs email and password)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for reading user data (excludes password hash)
class UserInDB(UserBase):
    id: int
    hashed_password: str

# Schema for returning user data to the client (excludes password hash)
# Renamed from 'User' to 'UserOut' to match expected import in routes.py
class UserOut(UserBase):
    id: int
    # No hashed_password field here, as we don't return it to the user

# --- Schemas for JWT Authentication ---

# Schema for the payload inside the JWT (used in app/utils/auth.py)
class TokenData(BaseModel):
    user_id: str | None = None

# Schema for the response returned after a successful login
class Token(BaseModel):
    access_token: str
    token_type: str
