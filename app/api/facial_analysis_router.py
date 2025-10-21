from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import base64
import cv2
import numpy as np
import logging

# Set up logger for this module
logger = logging.getLogger(__name__)

facial_analysis_router = APIRouter()

@facial_analysis_router.post('/analyze-expression')
async def analyze_expression(request: Request):
    """
    Receives an image, performs facial expression analysis, and returns results.
    """
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Error parsing request JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if not data or 'image' not in data:
        raise HTTPException(status_code=400, detail="No image data provided")

    image_data = data['image']
    # Remove the "data:image/jpeg;base64," prefix if present
    if "base64," in image_data:
        image_data = image_data.split("base64,")[1]

    try:
        # Decode base64 image
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise HTTPException(status_code=400, detail="Could not decode image")

        # Placeholder for facial analysis logic
        # In a real implementation, you would use a pre-trained model (e.g., OpenCV, Dlib, or an external API)
        # to detect faces and analyze expressions.
        
        expressions = ["Focused", "Neutral", "Engaged", "Thinking"]
        expression = np.random.choice(expressions)
        confidence = np.random.uniform(0.7, 0.95)

        return JSONResponse(content={'expression': expression, 'confidence': confidence, 'message': 'Facial analysis performed.'}, status_code=200)

    except HTTPException:
        raise # Re-raise HTTPExceptions
    except Exception as e:
        logger.error(f"Error during facial analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error during analysis: {e}")