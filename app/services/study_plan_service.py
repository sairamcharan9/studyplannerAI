import os
import logging
from typing import Dict, Any, List, Optional
from .research_service import ResearchService
from .gemini_service import GeminiService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyPlanService:
    """
    Service for generating study plans based on research data and user preferences
    """
    
    def __init__(self):
        self.research_service = ResearchService()
        self.gemini_service = GeminiService()
        
        self.ai_provider = "gemini"
        logger.info(f"Study plan service initialized with AI provider: {self.ai_provider}")
    
    async def generate_plan(self,
                          topic: str,
                          research_data: Dict[str, Any],
                          depth_level: int = 3,
                          duration_weeks: int = 4,
                          include_resources: bool = True,
                          learning_style: Optional[str] = None,
                          prior_knowledge: Optional[str] = None,
                          goals: Optional[List[str]] = None,
                          additional_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive study plan
        
        Args:
            topic: The main topic to create a study plan for
            research_data: Data collected from research
            depth_level: Level of detail (1-5)
            duration_weeks: Duration of the plan in weeks
            include_resources: Whether to include learning resources
            learning_style: Preferred learning style
            prior_knowledge: Level of prior knowledge
            goals: Specific learning goals
            additional_context: Any additional context or requirements
            
        Returns:
            Structured study plan as a dictionary
        """
        try:
            logger.info(f"Generating study plan for topic: {topic}")
            logger.info(f"Generation parameters: depth={depth_level}, duration={duration_weeks} weeks, learning_style={learning_style}, prior_knowledge={prior_knowledge}")
            
            use_ai = os.getenv("USE_AI_GENERATION", "true").lower() in ["true", "1", "yes"]
            
            if use_ai:
                logger.info(f"Attempting to generate study plan using Gemini model: {self.gemini_service.model}")
                study_plan = await self.gemini_service.create_study_plan(
                    topic=topic,
                    research_data=research_data,
                    duration_weeks=duration_weeks,
                    depth_level=depth_level,
                    learning_style=learning_style,
                    prior_knowledge=prior_knowledge
                )
                generation_method = "GEMINI"
            else:
                logger.warning(f"AI generation disabled by environment setting. Using PLACEHOLDER generation.")
                study_plan = self._create_fallback_plan(topic, duration_weeks)
                generation_method = "PLACEHOLDER"
            
            is_fallback = False
            if "summary" in study_plan and ("[FALLBACK TEMPLATE]" in study_plan["summary"] or "[PLACEHOLDER CONTENT]" in study_plan["summary"]):
                is_fallback = True
                generation_method = "PLACEHOLDER"
                
            if "summary" in study_plan and not is_fallback:
                study_plan["summary"] = f"[Generated using: {generation_method}] " + study_plan["summary"]
                
            if goals and isinstance(goals, list) and len(goals) > 0:
                if "learning_objectives" in study_plan:
                    existing_objectives = study_plan["learning_objectives"]
                    merged_objectives = list(set(existing_objectives + goals))
                    study_plan["learning_objectives"] = merged_objectives[:10]
            
            if additional_context and "recommendations" in study_plan:
                study_plan["recommendations"] += f"\n\nAdditional context considered: {additional_context}"
            
            if not include_resources and "resources" in study_plan:
                study_plan.pop("resources")
            
            if is_fallback or generation_method == "PLACEHOLDER":
                logger.info(f"Successfully generated study plan using PLACEHOLDER templates")
            else:
                model_name = self.gemini_service.model
                logger.info(f"Successfully generated study plan using Gemini with model: {model_name}")

            return study_plan
            
        except Exception as e:
            logger.error(f"Error generating study plan: {str(e)}")
            logger.warning(f"Falling back to template-based study plan generation for topic: {topic}")
            return self._create_fallback_plan(topic, duration_weeks)
    
    def _create_fallback_plan(self, topic: str, duration_weeks: int, is_fallback: bool = True) -> Dict[str, Any]:
        """
        Create a fallback study plan when generation fails
        """
        if is_fallback:
            logger.warning(f"FALLBACK MODE: Using BUILT-IN TEMPLATE generation (no AI model) for topic: {topic}")
        else:
            logger.info(f"PLACEHOLDER MODE: Using BUILT-IN TEMPLATE generation by configuration for topic: {topic}")
        weeks = [
            {"week": 1, "focus": "Fundamentals and Core Concepts"},
            {"week": 2, "focus": "Intermediate Concepts and Applications"},
            {"week": 3, "focus": "Advanced Topics and Practical Skills"},
            {"week": 4, "focus": "Projects and Real-world Implementation"}
        ]
        
        if duration_weeks < 4:
            weeks = weeks[:duration_weeks]
        elif duration_weeks > 4:
            for i in range(5, duration_weeks + 1):
                if i <= duration_weeks / 2:
                    weeks.append({"week": i, "focus": "Further Skills Development"})
                else:
                    weeks.append({"week": i, "focus": "Specialization and Mastery"})
        
        milestones = []
        for week in weeks:
            milestones.append({
                "title": f"Week {week['week']}: {week['focus']}",
                "description": f"Focus on {week['focus'].lower()} related to {topic}",
                "week": week['week'],
                "tasks": [
                    f"Study materials on {topic} {week['focus'].lower()}",
                    f"Complete practice exercises",
                    f"Review and solidify understanding"
                ],
                "estimated_hours": 10 + (week['week'] % 2)
            })
        
        return {
            "topic": topic,
            "summary": f"A structured {duration_weeks}-week study plan for mastering {topic}, covering fundamentals through advanced concepts.",
            "duration_weeks": duration_weeks,
            "learning_objectives": [
                f"Understand the core principles of {topic}",
                f"Develop practical skills in applying {topic}",
                f"Build projects that demonstrate mastery of {topic}",
                f"Establish a foundation for continued learning in {topic}"
            ],
            "key_concepts": [
                f"{topic} fundamentals",
                f"{topic} methodologies",
                f"{topic} best practices",
                f"{topic} applications"
            ],
            "milestones": milestones,
            "resources": [
                {
                    "title": f"{topic} - Comprehensive Guide",
                    "url": "",
                    "type": "book",
                    "description": "A thorough introduction to the subject"
                },
                {
                    "title": f"Practical {topic}",
                    "url": "",
                    "type": "online course",
                    "description": "Hands-on course with practical exercises"
                },
                {
                    "title": f"{topic} Community Forum",
                    "url": "",
                    "type": "community",
                    "description": "Connect with others studying the same topic"
                }
            ],
            "recommendations": "Focus on consistent daily practice. Alternate between theoretical study and practical application. Consider joining study groups or finding a mentor in this field."
        }
