from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from dotenv import dotenv_values, set_key
import os

router = APIRouter(tags=["settings"])
templates = Jinja2Templates(directory="templates")

def get_settings():
    # Load existing .env file or create an empty dict
    if os.path.exists(".env"):
        return dotenv_values(".env")
    return {}

def mask_api_key(api_key: str) -> str:
    """Masks an API key, showing only the first 8 characters."""
    if not api_key or len(api_key) < 8:
        return ""
    return f"{api_key[:8]}..."

@router.get("/settings", response_class=HTMLResponse)
async def get_settings_page(request: Request):
    settings = get_settings()
    # Mask API keys for security
    masked_settings = settings.copy()
    if "OPENROUTER_API_KEY" in masked_settings:
        masked_settings["OPENROUTER_API_KEY"] = mask_api_key(masked_settings["OPENROUTER_API_KEY"])
    if "GEMINI_API_KEY" in masked_settings:
        masked_settings["GEMINI_API_KEY"] = mask_api_key(masked_settings["GEMINI_API_KEY"])

    return templates.TemplateResponse("settings.html", {"request": request, "settings": masked_settings})

@router.post("/settings")
async def update_settings(form_data: dict):
    try:
        # Create .env file if it doesn't exist
        if not os.path.exists(".env"):
            with open(".env", "w") as f:
                pass  # Create an empty file

        # Handle unchecked checkbox
        if 'ENABLE_FACIAL_ANALYSIS' not in form_data:
            set_key(".env", "ENABLE_FACIAL_ANALYSIS", "false")

        # Update each key from the form
        for key, value in form_data.items():
            if value:  # Only update if a value is provided
                set_key(".env", key, value)

        return JSONResponse(content={"message": "Settings saved successfully"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Error saving settings: {str(e)}"}, status_code=500)
