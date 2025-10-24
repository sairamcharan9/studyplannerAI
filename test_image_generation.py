"""
Test script to verify image generation.
"""
import os
import asyncio
import logging
import httpx
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_image_generation")

async def test_image_generation():
    """Test image generation using the /api/generate-image endpoint"""
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        logger.error("OPENROUTER_API_KEY not set in .env file")
        return

    logger.info("====== Image Generation Test ======")

    test_prompt = "A futuristic cityscape"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/generate-image",
                json={"prompt": test_prompt},
                timeout=60.0
            )

            if response.status_code == 200:
                logger.info("Successfully generated image!")
                data = response.json()
                image_url = data.get("image_url")
                logger.info(f"Image URL: {image_url}")

                # TODO: Add a more robust check for the image URL
                assert image_url is not None and image_url != ""
            else:
                logger.error(f"Error generating image: {response.status_code}")
                logger.error(response.text)
                assert False, "Failed to generate image"

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        assert False, "An exception occurred during the test"

if __name__ == "__main__":
    # To run this test, make sure the FastAPI server is running:
    # uvicorn main:app --host 0.0.0.0 --port 8000
    # Then run this script in a separate terminal:
    # python test_image_generation.py
    asyncio.run(test_image_generation())
