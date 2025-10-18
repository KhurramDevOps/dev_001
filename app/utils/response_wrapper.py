from typing import Any, Optional, Union
from fastapi.encoders import jsonable_encoder

def api_response(
    data: Optional[Any] = None,
    message: str = "Success",
    status: bool = True,
    error: Optional[Union[str, dict]] = None
) -> dict:
    """
    Standardized API response wrapper.

    - Converts SQLAlchemy / Pydantic objects to JSON-safe format.
    - Avoids FastAPI validation errors.
    - Keeps consistent API structure.
    """

    safe_data = jsonable_encoder(data) if data is not None else None

    return {
        "status": status,
        "message": message,
        "data": safe_data,
        "error": error,
    }
