"""
Image service for StudyplannerAI.
Provides integration with OpenRouter API to generate images.
"""
import os
import logging
import httpx
from typing import Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageService:
    """
    Service for interacting with OpenRouter API to generate images.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        # TODO: Make the model configurable
        self.model = "google/gemini-flash-1.5-dev-latest"
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

        logger.info(f"Initialized ImageService with model: {self.model}")

    async def generate_image(self, prompt: str, height: Optional[int] = 1024, width: Optional[int] = 1024) -> str:
        """
        Generate an image using the OpenRouter API.

        Args:
            prompt: The prompt to send to the model.
            height: The height of the image.
            width: The width of the image.

        Returns:
            The URL of the generated image.
        """
        if not self.api_key:
            logger.error("OpenRouter API key is not set")
            raise ValueError("OpenRouter API key is not set in environment variables")

        try:
            logger.info(f"Generating image with prompt: {prompt}")

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://studyplannerai.app",
                "X-Title": "StudyplannerAI"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": f"Generate an image of {prompt}"}
                ],
                "modalities": ["image", "text"],
                "image_config": {
                    "height": height,
                    "width": width,
                }
            }

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers=headers,
                    json=payload
                )

                if response.status_code != 200:
                    logger.error(f"Error from OpenRouter API: {response.status_code}")
                    logger.error(f"Response body: {response.text}")
                    raise Exception(f"Error generating image: {response.status_code} - {response.text}")

                result = response.json()

                if result.get("choices"):
                    message = result["choices"][0]["message"]
                    if message.get("images"):
                        image_url = message["images"][0]["image_url"]["url"]
                        return image_url

                raise Exception("Image URL not found in response")

        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
