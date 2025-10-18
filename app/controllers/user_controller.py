from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.user_model import User
from ..db.database import get_db
from ..utils.response_wrapper import api_response
from ..schemas.user_schema import UserSchema , UserUpdate
from ..schemas.response_schema import APIResponse, UserResponse
from typing import List , Optional 

router= APIRouter()

@router.post("/users/", response_model = APIResponse[UserResponse]) 
def create_users(user:UserSchema, db:Session = Depends(get_db)):
    db_user = User(name= user.name, email = user.email)
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return api_response(data=db_user, message="User created successfully")


@router.get("/users/",response_model =APIResponse[List[UserResponse]] )
def read_users(skip:int = 0,limit:int =10 , db:Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return api_response(data=users, message="All Users retrieved")


@router.get("/users/{user_id}", response_model = APIResponse[UserResponse])
def read_user(user_id:int,db:Session=Depends(get_db)):
    user = db.query(User).filter(User.id ==user_id).first()
    if user is None:
        raise HTTPException(status_code = 404 , detail ="User not Found")
    return api_response(data=user, message="User retrieved successfully")


@router.put("/users/{user_id}", response_model= APIResponse[UserResponse])
def update_user(user_id : int , user: UserUpdate, db : Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None : 
        raise HTTPException(status_code = 404 , detail = "User not found ")
    db_user.name = user.name if user.name is not None else db_user.name
    db_user.email =user.email if user.email is not None else db_user.email
    db.commit()
    db.refresh(db_user)
    return api_response(data=db_user, message="User Updated successfully")


@router.delete("/users/{user_id}", response_model = APIResponse[UserResponse])
def delete_user(user_id:int , db : Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()

    if db_user is None:
        raise HTTPException(status_code = 404 , detail ="User not found")

    db.delete(db_user)
    db.commit()
    return api_response(data=db_user, message="User Deleted successfully")