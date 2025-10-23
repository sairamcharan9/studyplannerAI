import os
import logging
import sys
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import our app modules
from app.api.router import router as api_router
from app.api.settings_router import router as settings_router

# Load environment variables
load_dotenv()

# Set up logging configuration
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("studyplanner.log"),
    ]
)

logger = logging.getLogger("studyplanner")

# Log startup configuration
logger.info("Starting StudyplannerAI application")
logger.info(f"Log level set to: {log_level}")
logger.info(f"Using AI generation: {os.getenv('USE_AI_GENERATION', 'true')}")
logger.info(f"AI provider: {os.getenv('AI_PROVIDER', 'placeholder')}")

# Log provider-specific configuration
if os.getenv('AI_PROVIDER', '').lower() == 'openrouter':
    logger.info(f"OpenRouter model: {os.getenv('OPENROUTER_MODEL', 'Not set')}")
    # Mask API key for security
    api_key = os.getenv('OPENROUTER_API_KEY', '')
    masked_key = api_key[:8] + '...' if api_key else 'Not set'
    logger.info(f"OpenRouter API key: {masked_key}")
elif os.getenv('AI_PROVIDER', '').lower() == 'ollama':
    logger.info(f"Ollama model: {os.getenv('OLLAMA_MODEL', 'Not set')}")
    logger.info(f"Ollama host: {os.getenv('OLLAMA_HOST', 'Not set')}")
else:
    logger.info("Using placeholder generation (no AI)")


# Create FastAPI app
app = FastAPI(
    title="StudyplannerAI",
    description="AI-powered study plan generator based on research and user prompts",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router, prefix="/api")
app.include_router(settings_router)

# Root route
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "StudyplannerAI - Generate Research-Based Study Plans"}
    )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
