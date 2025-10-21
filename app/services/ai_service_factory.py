import os
import logging
from app.services.ollama_service import OllamaService
from app.services.openrouter_service import OpenRouterService

logger = logging.getLogger(__name__)

def get_ai_service():
    """
    Factory function to get the AI service based on the environment variable.
    """
    ai_provider = os.getenv("AI_PROVIDER", "ollama").lower()
    logger.info(f"AI_PROVIDER set to: {ai_provider}")

    if ai_provider == "openrouter":
        logger.info("Returning OpenRouterService")
        return OpenRouterService()
    elif ai_provider == "ollama":
        logger.info("Returning OllamaService")
        return OllamaService()
    else:
        logger.warning(f"Invalid AI_PROVIDER '{ai_provider}'. Using OllamaService as default.")
        return OllamaService()
