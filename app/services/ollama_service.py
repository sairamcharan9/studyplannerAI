import os
import logging
import ollama
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaService:
    """
    Service for interacting with the Ollama API
    """
    
    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")
        self.client = ollama.AsyncClient(host=self.host)
        logger.info(f"Ollama service initialized with host: {self.host} and model: {self.model}")
        
    async def generate_text(self, prompt: str, options: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Generate text using the Ollama API
        """
        try:
            logger.info("Generating text with Ollama")
            response = await self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            raise
