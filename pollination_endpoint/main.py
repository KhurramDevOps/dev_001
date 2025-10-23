import httpx
from urllib.parse import quote_plus
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# ----------------------------------------------------------------------
# 1. Initialization and Configuration
# ----------------------------------------------------------------------

app = FastAPI(
    title="Pollinations AI Keyless Proxy (Plain Text Output)",
    description="A non-blocking FastAPI wrapper for the free, keyless Pollinations AI Text API, using default plain text output for stability."
)

# Initialize the asynchronous client globally
client = httpx.AsyncClient(timeout=30.0) 

POLLINATIONS_BASE_URL = "https://text.pollinations.ai/prompt/"
# CRITICAL FIX: The POLLINATIONS_SUFFIX = "?json=true" has been removed 
# to prevent routing to the complex OpenAI backend that caused the 400 error.

# ----------------------------------------------------------------------
# 2. Input and Output Validation Schemas
# ----------------------------------------------------------------------

class PromptRequest(BaseModel):
    """Schema for the incoming request body."""
    question: str

class GenerationResponse(BaseModel):
    """Schema for the successful output response."""
    response: str
    
# ----------------------------------------------------------------------
# 3. Asynchronous API Endpoint (Corrected)
# ----------------------------------------------------------------------

@app.post("/generate", 
          response_model=GenerationResponse,
          summary="Generate text using Pollinations AI Keyless Endpoint (Plain Text)")
async def generate_text(prompt_data: PromptRequest):
    """
    Receives user question, performs mandatory URL encoding, and executes a 
    non-blocking GET request to the Pollinations API.
    """
    user_question = prompt_data.question
    
    # Mandatory Step: URL encoding for safe path transmission [1]
    encoded_prompt = quote_plus(user_question)
    
    # Construct the final URL (without any query parameters for simplest mode)
    full_url = f"{POLLINATIONS_BASE_URL}{encoded_prompt}"
    
    try:
        # Non-blocking asynchronous GET request
        response = await client.get(full_url)
        response.raise_for_status()
        
        # FIX: The API now returns raw plain text in the body 
        generated_text = response.text
        
        # Success: Return the text wrapped in a JSON object for the client
        return {"response": generated_text}
        
    except httpx.HTTPStatusError as e:
        # Handling upstream errors (e.g., 429 Rate Limit, or the previous 400)
        
        # Attempt to parse the upstream error response body as JSON
        try:
            error_detail = json.loads(e.response.text)
        except json.JSONDecodeError:
            # If it's not JSON, use the raw text
            error_detail = e.response.text
            
        raise HTTPException(
            status_code=502, # 502 Bad Gateway indicates upstream failure
            detail={
                "error": f"Upstream AI service failed with status code {e.response.status_code}",
                "upstream_detail": error_detail,
                "note": "The keyless tier is strictly rate-limited (1 concurrent req / 3 sec) ."
            }
        )
    
    except httpx.RequestError as e:
        # Handles network-level errors (e.g., DNS resolution, connection timeout)
        raise HTTPException(
            status_code=504, 
            detail={"error": f"Network error during request to Pollinations AI: {type(e).__name__}"}
        )