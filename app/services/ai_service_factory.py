import os
import logging
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

def get_ai_service():
    """
    Factory function to get the AI service.
    Always returns GeminiService as it's the sole AI provider.
    """
    logger.info("Returning GeminiService (sole AI provider)")
    return GeminiService()