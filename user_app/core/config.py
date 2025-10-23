from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# Calculate the absolute path to the project root and the .env file
# Path(__file__).resolve() points to this file. We go up two levels:
# config.py -> core -> app -> D:\gemini_user_management (Project Root)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = BASE_DIR / ".env"

# Using Pydantic's BaseSettings to manage settings/environment variables
class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./user_management.db"

    # JWT Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Configuration for loading from .env
    model_config = SettingsConfigDict(
        # Use the absolute path to ensure the .env file is found
        env_file=DOTENV_PATH, 
        extra='ignore' # Prevents warnings if extra fields are present
    )

# Use lru_cache for efficient, single-time loading of settings
@lru_cache()
def get_settings():
    # If the file exists, load it. If not, Pydantic will complain about missing fields.
    if not DOTENV_PATH.is_file():
        print(f"WARNING: .env file not found at {DOTENV_PATH}. Attempting to load environment variables directly.")

    return Settings()

settings = get_settings()
