from sqlalchemy.orm import Session
from app.modules.users.models import User
from app.modules.users.schemas import UserCreate
from app.utils.auth import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    """Retrieves a user by email."""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """Retrieves a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    """Creates a new user, hashing the password."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email, 
        hashed_password=hashed_password, 
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticates a user by email and password."""
    user = get_user_by_email(db, email=email)
    
    if user and verify_password(password, user.hashed_password):
        return user
    return None