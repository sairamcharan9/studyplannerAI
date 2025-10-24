from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

from app.services.image_service import ImageService

# Create router
router = APIRouter(tags=["images"])

# Pydantic models for request/response
class ImageGenerationRequest(BaseModel):
    prompt: str
    height: Optional[int] = 1024
    width: Optional[int] = 1024

class ImageGenerationResponse(BaseModel):
    image_url: str

# Dependency
def get_image_service():
    return ImageService()

# Routes
@router.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    image_service: ImageService = Depends(get_image_service),
):
    """
    Generate an image based on a prompt.
    """
    try:
        image_url = await image_service.generate_image(
            prompt=request.prompt,
            height=request.height,
            width=request.width
        )
        return ImageGenerationResponse(image_url=image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")
