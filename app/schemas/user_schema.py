from pydantic import BaseModel
from typing import Optional

class UserSchema(BaseModel):  # For request (input)
    name: str
    email: str

class UserResponse(BaseModel):  # For response (output)
    id: int
    name: str
    email: str
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    class Config:
        orm_mode = True

    
