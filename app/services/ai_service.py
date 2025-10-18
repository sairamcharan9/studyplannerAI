import os
import logging
import json
from typing import Dict, Any, List

# Import individual provider services
from .ollama_service import OllamaService
from .openrouter_service import OpenRouterService
# Import future provider services
# from .openai_service import OpenAIService
# from .gemini_service import GeminiService

logger = logging.getLogger(__name__)

class AIService:
    """
    Factory class to select and interact with the appropriate AI provider.
    """

    def __init__(self):
        self.provider_name = os.getenv("AI_PROVIDER", "ollama").lower()
        self.provider = self._get_provider()
        logger.info(f"AIService initialized with provider: {self.provider_name}")

    def _get_provider(self):
        """
        Selects the AI provider based on the environment variable.
        """
        if self.provider_name == "ollama":
            return OllamaService()
        elif self.provider_name == "openrouter":
            return OpenRouterService()
        # Add future providers here
        # elif self.provider_name == "openai":
        #     return OpenAIService()
        # elif self.provider_name == "gemini":
        #     return GeminiService()
        else:
            logger.error(f"Unsupported AI provider: {self.provider_name}")
            raise ValueError(f"Unsupported AI provider: {self.provider_name}")

    async def generate_text(self, prompt: str, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Generates text using the selected AI provider.
        """
        logger.info(f"Generating text with {self.provider_name}")
        response = await self.provider.generate_text(prompt, options)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"response": response}

    async def translate_text(self, text: str, target_language: str) -> str:
        """
        Translates text using the selected AI provider.
        """
        logger.info(f"Translating text to {target_language} with {self.provider_name}")
        prompt = f"Translate the following text to {target_language}: {text}"
        response = await self.generate_text(prompt)
        return response.get("translated_text", "")

    async def summarize_text(self, text: str) -> str:
        """
        Summarizes text using the selected AI provider.
        """
        logger.info(f"Summarizing text with {self.provider_name}")
        prompt = f"Summarize the following text: {text}"
        response = await self.generate_text(prompt)
        return response.get("summary", "")

    async def extract_keywords(self, text: str) -> List[str]:
        """
        Extracts keywords from text using the selected AI provider.
        """
        logger.info(f"Extracting keywords with {self.provider_name}")
        prompt = f"Extract the keywords from the following text: {text}"
        response = await self.generate_text(prompt)
        return response.get("keywords", [])

ai_service = AIService()
