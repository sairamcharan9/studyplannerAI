import os
import logging
from typing import Dict, Any, List, Optional
from .research_service import ResearchService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StudyPlanService:
    """
    Service for generating study plans based on research data and user preferences
    """
    
    def __init__(self):
        self.research_service = ResearchService()
        logger.info("Study plan service initialized")
    
    async def generate_plan(self,
                          ai_service: Any,
                          topic: str,
                          research_data: Dict[str, Any],
                          depth_level: int = 3,
                          duration_weeks: int = 4,
                          include_resources: bool = True,
                          learning_style: Optional[str] = None,
                          prior_knowledge: Optional[str] = None,
                          goals: Optional[List[str]] = None,
                          generate_goals: bool = False,
                          additional_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive study plan
        
        Args:
            ai_service: The AI service instance to use for generation.
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
            
            # Check if we're using AI or placeholders
            use_ai = os.getenv("USE_AI_GENERATION", "true").lower() in ["true", "1", "yes"]
            
            if use_ai:
                logger.info(f"Attempting to generate study plan using AI service: {ai_service.__class__.__name__}")
                study_plan = await ai_service.create_study_plan(
                    topic=topic,
                    research_data=research_data,
                    duration_weeks=duration_weeks,
                    depth_level=depth_level,
                    learning_style=learning_style,
                    prior_knowledge=prior_knowledge
                )
                generation_method = ai_service.__class__.__name__
            else:
                # Skip AI and use placeholders directly
                logger.warning(f"AI generation disabled by environment setting. Using PLACEHOLDER generation.")
                study_plan = self._create_fallback_plan(topic, duration_weeks)
                generation_method = "PLACEHOLDER"
            
            # Check if this is actually a fallback template by looking for markers in the summary
            is_fallback = False
            if "summary" in study_plan and ("[FALLBACK TEMPLATE]" in study_plan["summary"] or "[PLACEHOLDER CONTENT]" in study_plan["summary"]):
                is_fallback = True
                generation_method = "PLACEHOLDER"
                
            # Add generation method to the plan (only if not already marked by the fallback system)
            if "summary" in study_plan and not is_fallback:
                study_plan["summary"] = f"[Generated using: {generation_method}] " + study_plan["summary"]
                
            # Generate or merge goals
            if generate_goals:
                logger.info("Generating smart goals...")
                generated_goals = await self.generate_learning_goals(
                    ai_service=ai_service,
                    topic=topic,
                    duration_weeks=duration_weeks,
                    prior_knowledge=prior_knowledge
                )
                if "learning_objectives" in study_plan:
                    study_plan["learning_objectives"] = list(set(study_plan["learning_objectives"] + generated_goals))
                else:
                    study_plan["learning_objectives"] = generated_goals
            elif goals and isinstance(goals, list) and len(goals) > 0:
                if "learning_objectives" in study_plan:
                    # Merge user-provided goals with generated objectives
                    study_plan["learning_objectives"] = list(set(study_plan["learning_objectives"] + goals))
            
            # Add any additional context as recommendations
            if additional_context and "recommendations" in study_plan:
                study_plan["recommendations"] += f"\n\nAdditional context considered: {additional_context}"
            
            # Remove resources if not requested
            if not include_resources and "resources" in study_plan:
                study_plan.pop("resources")
            
            # Report the correct AI provider that was used
            if is_fallback or generation_method == "PLACEHOLDER":
                logger.info(f"Successfully generated study plan using PLACEHOLDER templates")
            else:
                model_name = getattr(ai_service, 'model', 'unknown')
                logger.info(f"Successfully generated study plan using {generation_method} with model: {model_name}")
                
            return study_plan
            
        except Exception as e:
            logger.error(f"Error generating study plan: {str(e)}")
            # Generate a fallback study plan
            logger.warning(f"Falling back to template-based study plan generation for topic: {topic}")
            return self._create_fallback_plan(topic, duration_weeks)

    async def generate_learning_goals(self, ai_service: Any, topic: str, duration_weeks: int, prior_knowledge: Optional[str]) -> List[str]:
        """
        Generate learning goals using the selected AI provider.
        """
        try:
            return await ai_service.generate_learning_goals(
                topic=topic,
                duration_weeks=duration_weeks,
                prior_knowledge=prior_knowledge
            )
        except Exception as e:
            logger.error(f"Failed to generate learning goals: {e}")
            return [
                f"Understand the core principles of {topic}",
                f"Develop practical skills in applying {topic}",
                f"Build a small project using {topic}"
            ]
    
    def _create_fallback_plan(self, topic: str, duration_weeks: int, is_fallback: bool = True) -> Dict[str, Any]:
        """
        Create a fallback study plan when generation fails
        """
        if is_fallback:
            logger.warning(f"FALLBACK MODE: Using BUILT-IN TEMPLATE generation (no AI model) for topic: {topic}")
        else:
            logger.info(f"PLACEHOLDER MODE: Using BUILT-IN TEMPLATE generation by configuration for topic: {topic}")
        # Simple fallback plan structure
        weeks = [
            {"week": 1, "focus": "Fundamentals and Core Concepts"},
            {"week": 2, "focus": "Intermediate Concepts and Applications"},
            {"week": 3, "focus": "Advanced Topics and Practical Skills"},
            {"week": 4, "focus": "Projects and Real-world Implementation"}
        ]
        
        # Adjust for requested duration
        if duration_weeks < 4:
            weeks = weeks[:duration_weeks]
        elif duration_weeks > 4:
            # Add additional weeks
            for i in range(5, duration_weeks + 1):
                if i <= duration_weeks / 2:
                    weeks.append({"week": i, "focus": "Further Skills Development"})
                else:
                    weeks.append({"week": i, "focus": "Specialization and Mastery"})
        
        # Build the milestones
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
                "estimated_hours": 10 + (week['week'] % 2)  # Alternate between 10 and 11 hours
            })
        
        # Construct the fallback plan
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
