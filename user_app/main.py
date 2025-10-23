from fastapi import FastAPI
from app.core.database import Base, engine
from app.modules.users import routes

# -----------------------------------------------------------------
# DATABASE INITIALIZATION HELPER
# Ensures all tables defined in your models are created in the database 
# when the application starts.
# -----------------------------------------------------------------
def create_tables_on_startup():
    """Create all defined tables in the database."""
    print("Attempting to create database tables...")
    # This command checks all models that inherit from Base and creates 
    # tables for them if they do not exist.
    Base.metadata.create_all(bind=engine)

# -----------------------------------------------------------------

app = FastAPI(
    title="Gemini User Management API",
    description="A simple API for user registration and authentication.",
    version="1.0.0",
)

# -----------------------------------------------------------------
# ⚠️ Startup Event: Call table creation here 
# -----------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    # Call the function to ensure tables exist
    create_tables_on_startup()


# Include the user routes router
app.include_router(routes.router, prefix="/users", tags=["users"])
