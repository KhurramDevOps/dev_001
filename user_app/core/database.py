from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Construct the database URL using the setting from the config module
# It should point to the SQLite file in your project root: sqlite:///./user_management.db
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Create the SQLAlchemy engine
# 'connect_args' is crucial for SQLite when working with FastAPI's multiple threads
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}, 
    # 'echo=True' prints the SQL queries to the console for debugging
    echo=True 
)

# Create a configured "Session" class
# This object will be used to create the actual database sessions
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

# Base class which all SQLAlchemy ORM models will inherit from
Base = declarative_base()


# Dependency function for FastAPI routes
def get_db():
    """
    Dependency that yields a new database session and ensures it is closed 
    after the request is finished. This is how FastAPI handles sessions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
