from fastapi import FastAPI
from .controllers.user_controller import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/api", tags=["users"])

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI CRUD API"}