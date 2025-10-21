import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service for interacting with Google Gemini API to generate study plans
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set. GeminiService will not be able to generate content.")
        else:
            genai.configure(api_key=self.api_key)

        logger.info(f"Initialized Gemini service with model: {self.model}")

    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using the Gemini API

        Args:
            prompt: The prompt to send to the model

        Returns:
            Generated text from the model
        """
        if not self.api_key:
            return "Error: GEMINI_API_KEY is not set."

        try:
            model = genai.GenerativeModel(self.model)
            response = await model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content with Gemini: {str(e)}")
            return f"Error: {str(e)}"

    async def create_study_plan(self,
                              topic: str,
                              research_data: Dict[str, Any],
                              duration_weeks: int = 4,
                              depth_level: int = 3,
                              learning_style: Optional[str] = None,
                              prior_knowledge: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a complete study plan using Gemini

        Args:
            topic: The main topic for the study plan
            research_data: Research data collected about the topic
            duration_weeks: Duration of the study plan in weeks
            depth_level: Level of detail (1-5)
            learning_style: Preferred learning style
            prior_knowledge: Level of prior knowledge

        Returns:
            Structured study plan
        """
        try:
            # Extract key information from research data to include in prompt
            sources_info = ""
            for idx, source in enumerate(research_data.get('sources', [])[:5]):
                sources_info += f"Source {idx+1}: {source.get('title', 'Unknown')} - {source.get('summary', '')[:300]}...\n\n"

            key_concepts = ", ".join(research_data.get('key_concepts', [])[:8])
            related_topics = ", ".join(research_data.get('related_topics', []))

            # Build the prompt
            prompt = f"""
You are an expert educational consultant creating a comprehensive study plan for the topic: {topic}.

RESEARCH DATA:
{sources_info}

KEY CONCEPTS: {key_concepts}

RELATED TOPICS: {related_topics}

PARAMETERS:
- Duration: {duration_weeks} weeks
- Depth Level: {depth_level}/5
- Learning Style: {learning_style if learning_style else 'Not specified'}
- Prior Knowledge: {prior_knowledge if prior_knowledge else 'Not specified'}

Create a detailed, structured study plan following this JSON format:
{{
  "topic": "The main topic",
  "summary": "A concise summary of what will be studied and why it's valuable",
  "duration_weeks": {duration_weeks},
  "learning_objectives": ["Objective 1", "Objective 2", "Objective 3", ...],
  "key_concepts": ["Concept 1", "Concept 2", "Concept 3", ...],
  "milestones": [
    {{
      "title": "Week 1: Foundation",
      "description": "Description of what will be covered",
      "week": 1,
      "tasks": ["Task 1", "Task 2", "Task 3", ...],
      "estimated_hours": 10
    }},
    ...more milestones for each week...
  ],
  "resources": [
    {{
      "title": "Resource Title",
      "url": "https://example.com/resource",
      "type": "article/book/video/course",
      "description": "Brief description of the resource"
    }},
    ...more resources...
  ],
  "recommendations": "Additional personalized recommendations based on learning style and prior knowledge. For instance, suggest hands-on projects for kinesthetic learners or foundational books for beginners."
}}

Return ONLY the valid JSON object, nothing else. Ensure all JSON is properly formatted and valid.
"""
            # Generate the study plan
            result = await self.generate_content(prompt)
            # Parse the JSON response
            try:
                # Find JSON content (in case there's additional text)
                json_start = result.find('{')
                json_end = result.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_content = result[json_start:json_end]
                    study_plan = json.loads(json_content)
                    logger.info(f"Successfully parsed AI-generated study plan for topic: {topic}")
                    return study_plan
                else:
                    logger.error("Could not find valid JSON in Gemini response")
                    return self._generate_fallback_plan(topic, duration_weeks)

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing JSON from Gemini response: {str(e)}")
                logger.error(f"Raw response: {result}")
                return self._generate_fallback_plan(topic, duration_weeks)

        except Exception as e:
            logger.error(f"Error creating study plan: {str(e)}")
            return self._generate_fallback_plan(topic, duration_weeks)

    async def generate_learning_goals(self, topic: str, duration_weeks: int, prior_knowledge: Optional[str]) -> List[str]:
        """
        Generate a list of learning goals using Gemini.
        """
        prompt = f"""
Based on the following information, generate 3-5 specific, actionable, and realistic learning goals for a study plan.

Topic: {topic}
Duration: {duration_weeks} weeks
Prior Knowledge: {prior_knowledge or 'None'}

Return a JSON list of strings. For example: ["goal 1", "goal 2", "goal 3"]
"""
        response = await self.generate_content(prompt)
        try:
            # Extract JSON from the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                goals_json = response[json_start:json_end]
                return json.loads(goals_json)
            return []
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from learning goals response.")
            return []

    def _generate_fallback_plan(self, topic: str, duration_weeks: int, is_disabled: bool = False) -> Dict[str, Any]:
        """
        Generate a fallback study plan when AI generation fails
        """
        if is_disabled:
            logger.warning(f"PLACEHOLDER MODE: Gemini generation disabled by configuration for topic: {topic}")
        else:
            logger.warning(f"FALLBACK MODE: Gemini generation failed, using template for topic: {topic}")

        # Create a basic template plan with clear indication it's a placeholder
        placeholder_indicator = "[PLACEHOLDER CONTENT] " if is_disabled else "[FALLBACK TEMPLATE] "

        return {{
            "topic": topic,
            "summary": f"{{placeholder_indicator}}A {{duration_weeks}}-week study plan for {{topic}}",
            "duration_weeks": duration_weeks,
            "learning_objectives": [
                f"Understand core concepts of {{topic}}",
                f"Develop practical skills in {{topic}}",
                f"Apply knowledge of {{topic}} to real-world scenarios"
            ],
            "key_concepts": [f"{{topic}} fundamentals", f"{{topic}} applications", f"{{topic}} best practices"],
            "milestones": [
                {{
                    "title": "Week 1: Fundamentals",
                    "description": f"Introduction to basic concepts of {{topic}}",
                    "week": 1,
                    "tasks": ["Research core concepts", "Study foundational principles", "Take beginner tutorial"],
                    "estimated_hours": 10
                }},
                {{
                    "title": f"Week {{duration_weeks//2}}: Intermediate Concepts",
                    "description": f"Deepen understanding of {{topic}}",
                    "week": duration_weeks//2,
                    "tasks": ["Work on practical exercises", "Study intermediate materials", "Begin small project"],
                    "estimated_hours": 12
                }},
                {{
                    "title": f"Week {{duration_weeks}}: Advanced Applications",
                    "description": f"Master advanced aspects of {{topic}}",
                    "week": duration_weeks,
                    "tasks": ["Complete project", "Review all materials", "Self-assessment"],
                    "estimated_hours": 15
                }}
            ],
            "resources": [
                {{
                    "title": f"{{topic}} - Official Documentation",
                    "url": "",
                    "type": "documentation",
                    "description": "Official documentation and guides"
                }},
                {{
                    "title": f"Introduction to {{topic}}",
                    "url": "",
                    "type": "course",
                    "description": "Beginner-friendly course"
                }}
            ],
            "recommendations": f"Focus on hands-on practice while studying {{topic}}. Consider joining relevant communities for support."
        }}
