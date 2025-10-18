import os
import logging
import httpx
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterService:
    """
    Service for interacting with the OpenRouter API
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "google/gemini-flash-1.5")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        logger.info(f"OpenRouter service initialized with model: {self.model}")

    async def generate_text(self, prompt: str, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Generate text using the OpenRouter API
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
            
        try:
            logger.info("Generating text with OpenRouter")
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                    },
                    timeout=120,
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error generating text with OpenRouter: {str(e)}")
            raise
