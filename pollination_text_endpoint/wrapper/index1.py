from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi import UploadFile, File
from pydantic import BaseModel
import requests
import logging
import os
import uuid
from fastapi.middleware.cors import CORSMiddleware
import io
import urllib.parse
import base64
from pydub import AudioSegment
from fastapi.responses import StreamingResponse
from pollinations import Text as PollinationsText
import pollinations  # the SDK
from dotenv import load_dotenv
load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
# Allowed origins (your React app)
origins = [
    "http://localhost:3000","http://localhost:3001"
    # you can add more, like "http://127.0.0.1:3000", or your domain in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # which origins are allowed
    allow_credentials=True,
    allow_methods=["*"],          # allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],          # allow all headers
)

# ---- Text models ----

class TextRequest(BaseModel):
    prompt: str

class TextResponse(BaseModel):
    result: str

@app.post("/wrapper-generate-text", response_model=TextResponse)
async def wrapper_generate_text(req: TextRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        text_model = pollinations.Text()
        result = text_model(prompt)
        # result is likely a string
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wrapper text generation error: {e}")
    return TextResponse(result=result)


# ---- Image models ----

class ImageRequest(BaseModel):
    prompt: str

class ImageResponse(BaseModel):
    filename: str
    filepath: str

IMAGES_DIR = "wrapper_generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

@app.post("/wrapper-generate-image", response_model=ImageResponse)
async def wrapper_generate_image(req: ImageRequest):
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        image_model = pollinations.Image()
        # Call it; by default it returns a PIL Image
        img = image_model(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Wrapper image generation error: {e}")

    # Save locally
    unique_name = str(uuid.uuid4()) + ".png"
    file_path = os.path.join(IMAGES_DIR, unique_name)
    try:
        img.save(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save image: {e}")

    return ImageResponse(filename=unique_name, filepath=file_path)

@app.get("/wrapper-images/{filename}")
async def serve_wrapper_image(filename: str):
    file_path = os.path.join(IMAGES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    # Determine media type (png or jpg depending on what SDK returns)
    return FileResponse(file_path, media_type="image/png")

# tts_extension.py

# class TextWithTTS(PollinationsText):
#     """
#     A subclass/adapter to add text-to-speech (mp3) support via Pollinations API.
#     """
#     def tts(self, text: str, voice: str = "alloy", model: str = "groq"):
#         if not text or not text.strip():
#             raise ValueError("Text is empty")

#         # URL-encode the prompt
#         enc = urllib.parse.quote(text, safe="")
#         url = f"https://text.pollinations.ai/{enc}"
#         params = {"model": model, "voice": voice}

#         # Optionally include auth header if your SDK or environment supports it
#         headers = {}
#         token = getattr(self, "token", None) or getattr(self, "_token", None)
#         if token:
#             headers["Authorization"] = f"Bearer {token}"

#         resp = requests.get(url, params=params, headers=headers, stream=True, timeout=30)
#         resp.raise_for_status()

#         return resp.iter_content(chunk_size=4096)

# tts_model = TextWithTTS()

# class TTSRequest(BaseModel):
#     text: str
#     voice: str = "nova"
#     model: str = "openai-audio"

# @app.post("/wrapper-tts")
# def wrapper_tts(req: TTSRequest):
#     if not req.text.strip():
#         raise HTTPException(status_code=400, detail="Text is empty")

#     try:
#         chunks = tts_model.tts(req.text, voice=req.voice, model=req.model)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"TTS call failed: {e}")

#     return StreamingResponse(chunks, media_type="audio/mpeg")


# class TTSRequest(BaseModel):
#     text: str
#     voice: str = "alloy"

# @app.post("/wrapper-tts")
# def wrapper_tts(req: TTSRequest):
#     text = req.text.strip()
#     if not text:
#         raise HTTPException(status_code=400, detail="Text is empty")

#     encoded = urllib.parse.quote(text, safe='')
#     url = f"https://text.pollinations.ai/{encoded}"
#     params = {"model": "openai-audio", "voice": req.voice}

#     token = os.getenv("POLLINATIONS_TOKEN")
#     logging.info(f"Using token: {token}")

#     headers = {}
#     if token:
#         headers["Authorization"] = f"Bearer {token}"
#         params["token"] = token  # optionally include as param too

#     logging.info("Wrapper TTS call")
#     logging.info(f"URL: {url}")
#     logging.info(f"Params: {params}")
#     logging.info(f"Headers: {headers}")

#     try:
#         resp = requests.get(url, params=params, headers=headers, stream=True, timeout=60)
#     except Exception as e:
#         logging.error(f"Request exception: {e}")
#         raise HTTPException(status_code=502, detail=f"Pollinations request error: {e}")

#     logging.info(f"Response status: {resp.status_code}")
#     logging.info(f"Response Content-Type: {resp.headers.get('Content-Type')}")
#     if resp.status_code != 200:
#         body_preview = ""
#         try:
#             body_preview = resp.text[:200]
#         except Exception:
#             pass
#         logging.error(f"Error body preview: {body_preview}")
#     try:
#         resp.raise_for_status()
#     except Exception as e:
#         raise HTTPException(status_code=resp.status_code, detail=f"TTS failed: {e}. Preview: {body_preview}")

#     ct = resp.headers.get("Content-Type", "")
#     if "audio/mpeg" not in ct:
#         preview = ""
#         try:
#             preview = resp.text[:200]
#         except:
#             pass
#         raise HTTPException(status_code=500, detail=f"Expected audio, got {ct}. Preview: {preview}")

#     return StreamingResponse(resp.iter_content(chunk_size=4096), media_type="audio/mpeg")




class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"

# Directory to save audio files
AUDIO_DIR = "wrapper_generated_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/wrapper-tts-save")
def wrapper_tts_save(req: TTSRequest):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is empty")

    # Build Pollinations TTS URL
    encoded = urllib.parse.quote(text, safe="")
    url = f"https://text.pollinations.ai/{encoded}"
    params = {
        "model": "openai-audio",
        "voice": req.voice
    }
    
    token = os.getenv("POLLINATIONS_TOKEN")
    logging.info(f"Using token: {token}")
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        # optionally also pass token in params
        params["token"] = token

    logging.info(f"TTS request URL: {url}")
    logging.info(f"Params: {params}")
    logging.info(f"Headers: {headers}")

    try:
        resp = requests.get(url, params=params, headers=headers, stream=True, timeout=60)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"TTS request failed: {e}")

    if resp.status_code != 200:
        # read small preview if error
        preview = None
        try:
            preview = resp.text[:200]
        except:
            preview = "<could not read preview>"
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"TTS failed. Status: {resp.status_code}. Preview: {preview}"
        )

    ct = resp.headers.get("Content-Type", "")
    if "audio/mpeg" not in ct:
        preview = None
        try:
            preview = resp.text[:200]
        except:
            preview = "<no preview>"
        raise HTTPException(status_code=500, detail=f"Unexpected content type: {ct}. Preview: {preview}")

    # Save audio to a file
    filename = f"{uuid.uuid4().hex}.mp3"
    file_path = os.path.join(AUDIO_DIR, filename)
    # Write the bytes to disk
    with open(file_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=4096):
            if chunk:
                f.write(chunk)

    # Option A: return the file for download
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)

    # Or Option B: stream the file back
    # with open(file_path, "rb") as f2:
    #     return StreamingResponse(f2, media_type="audio/mpeg")







@app.post("/wrapper-stt")
async def wrapper_stt(file: UploadFile = File(...)):
    """
    Accepts an uploaded audio file, optionally converts it to WAV,
    sends to Pollinations STT endpoint, and returns the transcription.
    """

    # Log incoming file metadata
    logger.info(f"Received file: filename={file.filename}, content_type={file.content_type}")

    # Derive extension
    name = file.filename
    if "." in name:
        ext = name.rsplit(".", 1)[1].lower()
    else:
        ext = ""  # unknown

    # Read raw bytes
    audio_bytes = await file.read()
    size = len(audio_bytes)
    logger.info(f"Audio bytes length: {size}")

    # Acceptable extensions list (you may expand)
    supported_ext = {"wav", "mp3", "ogg", "webm", "flac", "aac", "m4a"}

    if ext not in supported_ext:
        raise HTTPException(status_code=400, detail=f"Unsupported audio extension: {ext}")

    # If the audio is not already WAV, convert to WAV
    # We'll convert everything to WAV for consistency
    audio_for_encoding = None  # bytes to encode

    if ext == "wav":
        # Use original bytes
        audio_for_encoding = audio_bytes
        used_format = "wav"
        logger.info("No conversion needed (already WAV).")
    else:
        # Convert using pydub
        try:
            # Create a file-like object for input
            audio_seg = AudioSegment.from_file(io.BytesIO(audio_bytes), format=ext)
            wav_buf = io.BytesIO()
            audio_seg.export(wav_buf, format="wav")
            audio_for_encoding = wav_buf.getvalue()
            used_format = "wav"
            logger.info(f"Converted from {ext} to WAV, new size: {len(audio_for_encoding)} bytes")
        except Exception as e:
            logger.error(f"Audio conversion failed (ext={ext}): {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Audio conversion failed: {e}")

    # Base64 encode
    try:
        b64 = base64.b64encode(audio_for_encoding).decode("utf-8")
    except Exception as e:
        logger.error(f"Base64 encoding failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Base64 encoding failed: {e}")

    # Build payload for Pollinations STT
    payload = {
        "model": "openai-audio",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Transcribe this:"},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": b64,
                            "format": used_format
                        }
                    }
                ]
            }
        ]
    }
    logger.info("Payload ready for Pollinations STT (not logging full base64 for brevity)")

    # Prepare headers & auth
    headers = {"Content-Type": "application/json"}
    token = os.getenv("POLLINATIONS_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        # Optionally also include in payload or params if needed by API

    # Call Pollinations STT API
    try:
        resp = requests.post(
            "https://text.pollinations.ai/openai",
            headers=headers,
            json=payload,
            timeout=120
        )
        logger.info(f"Pollinations STT HTTP status: {resp.status_code}")
        resp.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        body = None
        try:
            body = resp.text
        except:
            body = "<could not read body>"
        logger.error(f"Pollinations STT HTTP error: {http_err}. Body: {body}")
        raise HTTPException(status_code=resp.status_code, detail=f"Pollinations STT failed: {body}")
    except Exception as e:
        logger.error(f"Pollinations STT request exception: {e}", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Pollinations STT request failed: {e}")

    # Parse response JSON
    try:
        j = resp.json()
        # The transcription should be in:
        # j["choices"][0]["message"]["content"]
        choices = j.get("choices", [])
        if not choices:
            logger.warning("Pollinations STT returned no choices")
            return {"transcription": ""}
        message = choices[0].get("message", {})
        transcription = message.get("content", "")
        logger.info(f"Transcription result: {transcription}")
        return {"filename": name, "transcription": transcription}
    except Exception as e:
        logger.error(f"Error parsing Pollinations response JSON: {e}. Raw response: {resp.text}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed parsing STT response: {e}")


# Image Analysis endpoint

@app.post("/wrapper-image-analyze")
async def wrapper_image_analyze(image: UploadFile = File(...)):
    """
    Accepts an image file, sends it to Pollinations vision API, returns description.
    """
    name = image.filename
    logger.info(f"Received image: {name}, content_type={image.content_type}")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Base64 encode
    try:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as e:
        logger.error("Base64 encoding failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Encoding image failed: {e}")

    # Build payload consistent with Pollinations “vision capabilities” spec
    payload = {
        "model": "openai",  # or image-capable model
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image:"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"}
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    headers = {"Content-Type": "application/json"}
    token = None  # get from env if needed
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.post("https://text.pollinations.ai/openai", headers=headers, json=payload, timeout=60)
        logger.info(f"Pollinations image-analysis status: {resp.status_code}")
        resp.raise_for_status()
    except requests.HTTPError as he:
        body = resp.text if resp is not None else "<no body>"
        logger.error(f"HTTP error from Pollinations: {he}, body: {body}")
        raise HTTPException(status_code=resp.status_code, detail=f"Image analysis failed: {body}")
    except Exception as e:
        logger.error("Error calling Pollinations image analysis", exc_info=True)
        raise HTTPException(status_code=502, detail=f"Vision request failed: {e}")

    # Parse response
    try:
        j = resp.json()
        choices = j.get("choices", [])
        if not choices:
            logger.warning("No choices returned in image analysis")
            return {"description": ""}
        message = choices[0].get("message", {})
        description = message.get("content", "")
        logger.info(f"Image analysis result: {description}")
        return {"filename": name, "description": description}
    except Exception as e:
        logger.error("Error parsing image analysis response", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed parsing analysis response: {e}")


# List TExt Models Endpoint

@app.get("/wrapper-list-text-models")
def wrapper_list_text_models():
    url = "https://text.pollinations.ai/models"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch models: {e}")

    try:
        data = resp.json()
    except Exception as e:
        logger.error(f"Error parsing models JSON: {e}, raw: {resp.text}")
        raise HTTPException(status_code=500, detail="Invalid JSON response from models endpoint")

    return data


# List Image Models Endpoint
@app.get("/wrapper-list-image-models")
def wrapper_image_models():
    url = "https://image.pollinations.ai/models"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching image models: {e}")
        raise HTTPException(status_code=502, detail=f"Failed to fetch image models: {e}")
    try:
        return resp.json()
    except Exception as e:
        logger.error(f"Error parsing image models JSON: {e}, raw: {resp.text}")
        raise HTTPException(status_code=500, detail="Invalid JSON from image models endpoint")

