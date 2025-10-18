
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx  
import os 
import uuid 
import urllib.parse
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allowed origins (your React app)
origins = [
    "http://localhost:3000",
    # you can add more, like "http://127.0.0.1:3000", or your domain in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # which origins are allowed
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # allow all headers
)



class TextRequest(BaseModel):
    prompt: str

class TextResponse(BaseModel):
    result: str

POLLINATIONS_BASE = "https://text.pollinations.ai"

@app.post("/generate-text", response_model=TextResponse)
async def generate_text(req: TextRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    # Encode prompt for URL
    # You may need to URL-encode spaces etc.
    import urllib.parse
    encoded = urllib.parse.quote(prompt)
    url = f"{POLLINATIONS_BASE}/{encoded}"

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=20.0)
    if resp.status_code != 200:
        # You might want more error details
        raise HTTPException(status_code=resp.status_code, detail=f"Pollinations API error: {resp.text}")
    text = resp.text  # Pollinations returns plain text (not JSON) for GET
    return TextResponse(result=text)

 
class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    filename: str
    filepath: str
    # you could also include a URL if you serve static files
    # image_url: Optional[str] = None

# Directory to store images
IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

POLLINATIONS_IMAGE_BASE = "https://pollinations.ai/p"  # from Pollinations docs :contentReference[oaicite:0]{index=0}

@app.post("/generate-image", response_model=ImageResponse)
async def generate_image(req: ImageRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # URL-encode prompt so special chars are safe
    encoded = urllib.parse.quote(prompt, safe="")  # encode all unsafe
    url = f"{POLLINATIONS_IMAGE_BASE}/{encoded}"

    # Make GET request to Pollinations
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout=60.0)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Image API error: {resp.text}")

    # Get image bytes
    image_bytes = resp.content
    if not image_bytes:
        raise HTTPException(status_code=500, detail="Empty image response")

    # Save to local file
    # Use uuid to avoid name collisions
    unique_name = str(uuid.uuid4()) + ".jpg"  # or .png based on what Pollinations returns
    file_path = os.path.join(IMAGES_DIR, unique_name)
    try:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

    # Return info to user
    return ImageResponse(filename=unique_name, filepath=file_path)

# (Optional) an endpoint to serve the saved image
@app.get("/images/{filename}")
async def serve_image(filename: str):
    file_path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    # Return the image as file response
    return FileResponse(file_path, media_type="image/jpeg")
