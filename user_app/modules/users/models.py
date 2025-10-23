from sqlalchemy import Column, Integer, String
from app.core.database import Base # Imports the Base class we just verified

# This is the SQLAlchemy ORM model definition
class User(Base):
    """
    SQLAlchemy model for the 'users' table.
    It inherits from the Base class defined in app/core/database.py
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), unique=True, index=True, nullable=False)
    full_name = Column(String(256), nullable=True)
    hashed_password = Column(String(256), nullable=False)
    
    # Optional: A useful representation for debugging
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
