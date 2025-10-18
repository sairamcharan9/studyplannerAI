import os
import logging
from typing import Dict, Any, List, Optional
from .research_service import ResearchService
from .ai_service import AIService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyPlanService:
    """
    Service for generating study plans based on research data and user preferences
    """
    
    def __init__(self):
        self.research_service = ResearchService()
        
    async def generate_plan(self,
                          topic: str,
                          research_data: Dict[str, Any],
                          ai_service: AIService,
                          depth_level: int = 3,
                          duration_weeks: int = 4,
                          include_resources: bool = True,
                          learning_style: Optional[str] = None,
                          prior_knowledge: Optional[str] = None,
                          goals: Optional[List[str]] = None,
                          additional_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive study plan
        """
        try:
            logger.info(f"Generating study plan for topic: {topic}")
            logger.info(f"Generation parameters: depth={depth_level}, duration={duration_weeks} weeks, learning_style={learning_style}, prior_knowledge={prior_knowledge}")
            
            use_ai = os.getenv("USE_AI_GENERATION", "true").lower() in ["true", "1", "yes"]
            
            if use_ai:
                options = {
                    "depth_level": depth_level,
                    "duration_weeks": duration_weeks,
                    "learning_style": learning_style,
                    "prior_knowledge": prior_knowledge,
                }
                prompt = self._create_prompt(topic, research_data, options)
                study_plan = await ai_service.generate_text(prompt, options)
                generation_method = ai_service.provider_name.upper()
            else:
                logger.warning(f"AI generation disabled. Using PLACEHOLDER generation.")
                study_plan = self._create_fallback_plan(topic, duration_weeks)
                generation_method = "PLACEHOLDER"
            
            is_fallback = "[FALLBACK TEMPLATE]" in study_plan.get("summary", "")
            if is_fallback:
                generation_method = "PLACEHOLDER"
                
            if "summary" in study_plan and not is_fallback:
                study_plan["summary"] = f"[Generated using: {generation_method}] " + study_plan["summary"]
                
            if goals:
                study_plan["learning_objectives"] = list(set(study_plan.get("learning_objectives", []) + goals))[:10]
            
            if additional_context:
                study_plan["recommendations"] = study_plan.get("recommendations", "") + f"\n\nAdditional context: {additional_context}"
            
            if not include_resources:
                study_plan.pop("resources", None)

            # Add new AI features
            study_plan['prerequisites'] = await self._get_prerequisites(topic, ai_service)
            study_plan['quiz'] = await self._generate_quiz(topic, study_plan, ai_service)
            
            logger.info(f"Successfully generated study plan using {generation_method}")
            return study_plan
            
        except Exception as e:
            logger.error(f"Error in generate_plan: {str(e)}")
            return self._create_fallback_plan(topic, duration_weeks)
    
    def _create_prompt(self, topic: str, research_data: Dict[str, Any], options: Dict[str, Any]) -> str:
        """
        Creates a prompt for the AI model to generate a study plan.
        """
        prompt = f"Create a detailed study plan for the topic: {topic}.\n"
        prompt += f"Duration: {options['duration_weeks']} weeks.\n"
        prompt += f"Detail Level: {options['depth_level']}/5.\n"
        if options['learning_style']:
            prompt += f"Adapt for a {options['learning_style']} learning style.\n"
        if options['prior_knowledge']:
            prompt += f"Assume {options['prior_knowledge']} level of prior knowledge.\n"
        prompt += f"Research data:\n{research_data}\n"
        prompt += "Include sections for summary, learning objectives, key concepts, milestones with tasks and estimated hours, and resource recommendations."
        return prompt

    async def _get_prerequisites(self, topic: str, ai_service: AIService) -> List[str]:
        """
        Identifies prerequisites for a given topic.
        """
        try:
            prompt = f"What are the prerequisites for learning {topic}?"
            response = await ai_service.generate_text(prompt)
            return response.get("prerequisites", [])
        except Exception as e:
            logger.error(f"Error getting prerequisites: {str(e)}")
            return ["Basic understanding of the field."]

    async def _generate_quiz(self, topic: str, study_plan: Dict[str, Any], ai_service: AIService) -> List[Dict[str, Any]]:
        """
        Generates a quiz based on the study plan.
        """
        try:
            concepts = ", ".join(study_plan.get("key_concepts", []))
            prompt = f"Create a 5-question multiple-choice quiz on the following concepts related to {topic}: {concepts}."
            response = await ai_service.generate_text(prompt)
            return response.get("quiz", [])
        except Exception as e:
            logger.error(f"Error generating quiz: {str(e)}")
            return [{"question": "Quiz generation failed.", "options": [], "answer": ""}]

    def _create_fallback_plan(self, topic: str, duration_weeks: int) -> Dict[str, Any]:
        """
        Create a fallback study plan when generation fails
        """
        logger.warning(f"FALLBACK MODE: Using BUILT-IN TEMPLATE for topic: {topic}")
        weeks = [{"week": i+1, "focus": "Core Concepts"} for i in range(duration_weeks)]
        
        milestones = [{
            "title": f"Week {w['week']}: {w['focus']}",
            "description": f"Focus on {w['focus'].lower()} of {topic}",
            "week": w['week'],
            "tasks": ["Task 1", "Task 2"],
            "estimated_hours": 10
        } for w in weeks]
        
        return {
            "topic": topic,
            "summary": f"[FALLBACK TEMPLATE] A structured {duration_weeks}-week plan for {topic}.",
            "duration_weeks": duration_weeks,
            "learning_objectives": [f"Understand {topic}", "Apply concepts"],
            "key_concepts": ["Concept 1", "Concept 2"],
            "milestones": milestones,
            "resources": [{"title": "Introductory Book", "type": "book"}],
            "recommendations": "Focus on fundamentals."
        }
