"""
Test script to verify SMART goals generation
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
logger = logging.getLogger("test_goals")

# Import services
from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service_factory import get_ai_service

async def test_smart_goals_generation():
    """Test SMART goals generation"""
    # Load environment variables
    load_dotenv()

    # Log current settings
    use_ai = os.getenv("USE_AI_GENERATION", "true").lower() in ["true", "1", "yes"]
    ai_provider = os.getenv("AI_PROVIDER", "ollama")

    logger.info("====== SMART Goals Test ======")
    logger.info(f"USE_AI_GENERATION = {os.getenv('USE_AI_GENERATION', 'true')}")
    logger.info(f"AI_PROVIDER = {ai_provider}")
    logger.info(f"Will use AI? {use_ai}")

    # Create services
    research_service = ResearchService()
    study_plan_service = StudyPlanService()
    ai_service = get_ai_service()

    # Topic to test with
    test_topic = "Creative Writing"

    # Perform a simple search to get research data
    logger.info(f"Researching topic: {test_topic}")
    try:
        research_data = await research_service.research_topic(test_topic, depth=1)

        # Generate study plan with SMART goals enabled
        logger.info(f"Generating study plan with SMART goals for topic: {test_topic}")
        study_plan = await study_plan_service.generate_plan(
            ai_service=ai_service,
            topic=test_topic,
            research_data=research_data,
            depth_level=3,
            duration_weeks=4,
            generate_goals=True
        )

        # Print the resulting plan
        logger.info("Generation successful!")
        logger.info(f"Summary: {study_plan.get('summary', 'No summary available')}")

        # Verify that learning objectives were generated
        learning_objectives = study_plan.get('learning_objectives', [])
        logger.info(f"Generated {len(learning_objectives)} learning objectives.")
        assert len(learning_objectives) > 0, "No learning objectives were generated"

        # Save to a file for inspection
        with open("goals_test_output.json", "w") as f:
            json.dump(study_plan, f, indent=2)
            logger.info("Saved study plan to goals_test_output.json")

    except Exception as e:
        logger.error(f"Error during test: {str(e)}")
        assert False, f"Test failed with exception: {e}"

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_smart_goals_generation())
