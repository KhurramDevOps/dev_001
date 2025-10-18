from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel
from pydantic.generics import GenericModel
from .user_schema import UserSchema

T = TypeVar("T")

class APIResponse(GenericModel, Generic[T]):
    status: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

    model_config = {"from_attributes": True}

class UserResponse(BaseModel):   # response for a single user
    id: int            # if Option A (UUID) -> str; if Option B (int) -> int
    name: str
    email: str

    model_config = {"from_attributes": True}
