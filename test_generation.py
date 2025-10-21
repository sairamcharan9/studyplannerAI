"""
Test script to verify study plan generation and logging
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
logger = logging.getLogger("test_generation")

# Import services
from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service_factory import get_ai_service

async def test_study_plan_generation():
    """Test study plan generation with current settings"""
    # Load environment variables
    load_dotenv()
    
    # Log current settings
    use_ai = os.getenv("USE_AI_GENERATION", "true").lower() in ["true", "1", "yes"]
    ai_provider = os.getenv("AI_PROVIDER", "ollama")
    
    logger.info("====== StudyplannerAI Test ======")
    logger.info(f"USE_AI_GENERATION = {os.getenv('USE_AI_GENERATION', 'true')}")
    logger.info(f"AI_PROVIDER = {ai_provider}")
    logger.info(f"Will use AI? {use_ai}")
    
    # Create services
    research_service = ResearchService()
    study_plan_service = StudyPlanService()
    ai_service = get_ai_service()
    
    # Topic to test with
    test_topic = "Python Programming"
    
    # Perform a simple search to get research data
    logger.info(f"Researching topic: {test_topic}")
    try:
        research_data = await research_service.research_topic(test_topic, depth=1)
        
        # Generate study plan
        logger.info(f"Generating study plan for topic: {test_topic}")
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
        
        # Determine type of generation by looking for placeholder markers
        generation_type = "PLACEHOLDER" if any(marker in study_plan.get('summary', '') 
                                           for marker in ['[PLACEHOLDER', '[FALLBACK']) else "AI"
        logger.info(f"Type of generation: {generation_type}")
        
        # Save to a file for inspection
        with open("test_plan_output.json", "w") as f:
            json.dump(study_plan, f, indent=2)
            logger.info("Saved study plan to test_plan_output.json")
            
    except Exception as e:
        logger.error(f"Error during test: {str(e)}")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_study_plan_generation())
