"""
Test script for verifying OpenRouter (Gemini) integration.
"""
import os
import asyncio
import logging
import json
import pytest
from dotenv import load_dotenv

# Set up logging to capture output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_openrouter")

# Import our services
from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service import AIService

@pytest.mark.asyncio
async def test_openrouter_generation():
    """Test generation using OpenRouter API"""
    # Load environment variables and configure for OpenRouter
    load_dotenv()
    os.environ["AI_PROVIDER"] = "openrouter"
    
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY is not set. Skipping OpenRouter test.")
        pytest.skip("OPENROUTER_API_KEY is not set.")
        return

    logger.info("====== OpenRouter Generation Test ======")
    
    # Initialize services
    research_service = ResearchService()
    study_plan_service = StudyPlanService()
    ai_service = AIService()
    
    # Define test parameters
    test_topic = "Quantum Computing"
    
    logger.info(f"Researching topic: {test_topic}")
    try:
        # Get some research data
        research_data = await research_service.research_topic(test_topic, depth=1)
        
        # Generate the study plan
        logger.info("Generating study plan with OpenRouter...")
        study_plan = await study_plan_service.generate_plan(
            topic=test_topic,
            research_data=research_data,
            ai_service=ai_service,
            duration_weeks=1,  # Keep it short for testing
            depth_level=2
        )
        
        # Log results
        logger.info("Study plan generation successful!")
        logger.info(f"Summary: {study_plan.get('summary', 'No summary provided')}")
        
        # Verify that OpenRouter was used
        assert "OPENROUTER" in study_plan.get('summary', ''), "Generation method not correctly attributed"
        
        # Save output for inspection
        with open("test_openrouter_output.json", "w") as f:
            json.dump(study_plan, f, indent=2)
            logger.info("Saved OpenRouter plan to test_openrouter_output.json")
            
    except Exception as e:
        logger.error(f"Error during OpenRouter test: {str(e)}")
        pytest.fail(f"Test failed with exception: {e}")

if __name__ == "__main__":
    # To run this test directly
    asyncio.run(test_openrouter_generation())
