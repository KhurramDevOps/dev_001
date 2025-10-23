from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

# Import all components
from app.modules.users import repository
from app.modules.users.schemas import UserCreate, UserLogin, UserOut, Token
from app.core.database import get_db
from app.core.config import settings
from app.utils.auth import create_access_token, get_current_user_id

router = APIRouter()

# -----------------
# SIGNUP Endpoint
# -----------------
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup_user(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    db_user = repository.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return repository.create_user(db=db, user=user)

# -----------------
# LOGIN Endpoint (Returns JWT Token)
# -----------------
@router.post("/login", response_model=Token)
def login_for_access_token(user_login: UserLogin, db: Session = Depends(get_db)):
    """Authenticates a user and returns a JWT access token."""
    
    # 1. Authenticate the user
    user = repository.authenticate_user(
        db, 
        email=user_login.email, 
        password=user_login.password
    )
    
    # 2. Handle failure
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Generate Token upon successful authentication
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    # 4. Return the token
    return {"access_token": access_token, "token_type": "bearer"}

# -----------------
# PROTECTED Endpoint (Requires Token)
# -----------------
@router.get("/me", response_model=UserOut)
def read_users_me(
    # The get_current_user_id dependency validates the token and extracts the ID
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Retrieves details of the currently authenticated user."""
    user = repository.get_user_by_id(db, user_id=current_user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user