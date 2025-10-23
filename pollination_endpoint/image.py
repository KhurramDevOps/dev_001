import httpx
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import json

# ----------------------------------------------------------------------
# 1. Initialization and Configuration
# ----------------------------------------------------------------------

app = FastAPI(
    title="Pollinations AI Keyless Proxy (Text & Image)",
    description="A non-blocking FastAPI wrapper for the free, keyless Pollinations AI APIs. Adheres to the 1 req / 3 sec rate limit."
)

# Initialize the asynchronous client globally
client = httpx.AsyncClient(timeout=30.0) 

# Separate base URLs for Text and Image endpoints [1, 2]
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/prompt/"
POLLINATIONS_IMAGE_URL = "https://image.pollinations.ai/prompt/" 

# ----------------------------------------------------------------------
# 2. Input and Output Validation Schemas
# ----------------------------------------------------------------------

class PromptRequest(BaseModel):
    """Schema for the incoming request body (used for both text and image)."""
    question: str

class GenerationResponse(BaseModel):
    """Schema for the successful text output response."""
    response: str
    
# ----------------------------------------------------------------------
# 3. Text Generation Endpoint: /generate
# ----------------------------------------------------------------------

@app.post("/generate", 
          response_model=GenerationResponse,
          summary="Generate text using Pollinations AI Keyless Endpoint")
async def generate_text(prompt_data: PromptRequest):
    """
    Handles text generation. Returns a structured JSON object containing the text.
    """
    user_question = prompt_data.question
    
    # Mandatory Step: URL encoding is crucial for safe path transmission [3]
    encoded_prompt = quote_plus(user_question)
    
    # Construct the final URL (uses the text base URL)
    full_url = f"{POLLINATIONS_TEXT_URL}{encoded_prompt}"
    
    try:
        # Non-blocking asynchronous GET request
        response = await client.get(full_url)
        response.raise_for_status()
        
        # The API returns raw plain text in the body 
        generated_text = response.text
        
        return {"response": generated_text}
        
    except httpx.HTTPStatusError as e:
        # Handling upstream HTTP errors (like 429 Rate Limit [1])
        try:
            error_detail = json.loads(e.response.text)
        except json.JSONDecodeError:
            error_detail = e.response.text
            
        raise HTTPException(
            status_code=502, # 502 Bad Gateway indicates upstream failure
            detail={
                "error": f"Upstream AI service failed with status code {e.response.status_code}",
                "upstream_detail": error_detail,
                "note": "The keyless tier is strictly rate-limited (1 concurrent req / 3 sec)."
            }
        )
    
    except httpx.RequestError as e:
        # Handling network errors (e.g., DNS, timeout)
        raise HTTPException(
            status_code=504, 
            detail={"error": f"Network error during request to Pollinations AI: {type(e).__name__}"}
        )

# ----------------------------------------------------------------------
# 4. Image Generation Endpoint: /generate-image
# ----------------------------------------------------------------------

@app.post("/generate-image", 
          # response_class must be Response because we are returning raw binary data
          response_class=Response, 
          summary="Generate an image and return the raw binary file (JPEG)")
async def generate_image(prompt_data: PromptRequest):
    """
    Handles image generation, returning the raw binary image data directly to the client.
    """
    user_question = prompt_data.question
    
    # Mandatory Step: URL encoding remains essential for path safety [3]
    encoded_prompt = quote_plus(user_question)
    
    # Construct the final image generation URL (uses the image base URL) [1]
    full_url = f"{POLLINATIONS_IMAGE_URL}{encoded_prompt}"
    
    try:
        # Non-blocking asynchronous GET request
        response = await client.get(full_url)
        response.raise_for_status()
        
        # We return a FastAPI Response object, setting the content to the raw binary data
        # and explicitly declaring the media_type (Content-Type) as image/jpeg.
        return Response(content=response.content, media_type="image/jpeg") 
        
    except httpx.HTTPStatusError as e:
        # Error handling for upstream failures
        raise HTTPException(
            status_code=502, 
            detail={
                "error": f"Upstream AI Image service failed with status code {e.response.status_code}",
                "upstream_detail": e.response.text, 
                "note": "The keyless tier is strictly rate-limited (1 concurrent req / 3 sec)."
            }
        )
    
    except httpx.RequestError as e:
        # Network error handling
        raise HTTPException(
            status_code=504, 
            detail={"error": f"Network error during request to Pollinations AI: {type(e).__name__}"}
        )