"""
Test script to verify Gemini integration
"""
import os
import asyncio
import logging
import json
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_gemini")

# Import services
from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service_factory import get_ai_service

async def test_gemini_generation():
    """Test study plan generation using Gemini"""
    # Load environment variables
    load_dotenv()

    # Override provider to ensure we use Gemini
    os.environ["AI_PROVIDER"] = "gemini"

    # Log current settings
    api_key = os.getenv("GEMINI_API_KEY", "")
    model = os.getenv("GEMINI_MODEL", "")

    # Create a masked version of the API key for logging (show only first 8 chars)
    masked_key = api_key[:8] + "..." if api_key else "Not set"

    logger.info("====== Gemini Integration Test ======")
    logger.info(f"GEMINI_API_KEY = {masked_key}")
    logger.info(f"GEMINI_MODEL = {model}")
    logger.info(f"AI_PROVIDER = {os.getenv('AI_PROVIDER')}")

    if not api_key:
        logger.error("Gemini API key not set in .env file")
        return

    # Create services
    research_service = ResearchService()
    study_plan_service = StudyPlanService()
    ai_service = get_ai_service()

    # Topic to test with
    test_topic = "Quantum Computing for Beginners"

    # Perform a simple search to get research data
    logger.info(f"Researching topic: {test_topic}")
    try:
        research_data = await research_service.research_topic(test_topic, depth=1)

        # Generate study plan
        logger.info(f"Generating study plan with Gemini for topic: {test_topic}")
        study_plan = await study_plan_service.generate_plan(
            ai_service=ai_service,
            topic=test_topic,
            research_data=research_data,
            depth_level=3,
            duration_weeks=4
        )

        # Print the resulting plan
        logger.info("Generation successful!")
        logger.info(f"Summary: {study_plan.get('summary', 'No summary available')}")

        # Determine type of generation
        if any(marker in study_plan.get('summary', '') for marker in ['[PLACEHOLDER', '[FALLBACK']):
            logger.info("Type of generation: PLACEHOLDER/FALLBACK (AI generation failed)")
        else:
            logger.info(f"Type of generation: GEMINI")

            # Print a few learning objectives to verify content
            objectives = study_plan.get('learning_objectives', [])
            if objectives:
                logger.info("Sample learning objectives:")
                for i, obj in enumerate(objectives[:3]):
                    logger.info(f"  {i+1}. {obj}")

        # Save to a file for inspection
        with open("gemini_test_output.json", "w") as f:
            json.dump(study_plan, f, indent=2)
            logger.info("Saved study plan to gemini_test_output.json")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_gemini_generation())
