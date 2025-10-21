"""
Gemini service for StudyplannerAI.
Provides integration with Gemini API to generate content using various AI models.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

import httpx

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service for interacting with Gemini API to generate study plans
    """
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "google/gemini-2.0-flash-exp:free")
        logger.info(f"Using model: {self.model}")
        
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.max_tokens = 4000
        self.temperature = 0.7
        
        logger.info(f"Initialized Gemini service")
        logger.info(f"Using AI model: {self.model}")
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using the Gemini API
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text from the model
        """
        masked_key = self.api_key[:8] + "..." if self.api_key else "Not set"
        logger.info(f"Gemini credentials - API Key: {masked_key}, Model: {self.model}")
        
        if not self.api_key:
            logger.error("Gemini API key is not set")
            return "Error: Gemini API key is not set in environment variables"
            
        try:
            logger.info(f"Generating content with Gemini model: {self.model}")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://studyplannerai.app",
                "X-Title": "StudyplannerAI"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are an expert educational consultant who creates comprehensive study plans. You always respond with valid, properly formatted JSON data as requested."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "stream": False
            }
            
            logger.info(f"Sending request to Gemini API")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                try:
                    response = await client.post(
                        self.api_url, 
                        headers=headers,
                        json=payload,
                        timeout=60.0
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"Error from Gemini API: {response.status_code}")
                        logger.error(f"Response body: {response.text}")
                        error_msg = "Unknown error"
                        try:
                            error_data = response.json()
                            if 'error' in error_data and 'message' in error_data['error']:
                                error_msg = error_data['error']['message']
                        except:
                            error_msg = response.text[:200]
                            
                        return f"Error generating content: {response.status_code} - {error_msg}"
                    
                    logger.info("Successfully received response from Gemini API")
                    
                    try:
                        result = response.json()
                        
                        if 'choices' in result and len(result['choices']) > 0:
                            choice = result['choices'][0]
                            if 'message' in choice and 'content' in choice['message']:
                                generated_text = choice['message']['content']
                                logger.info(f"Received {len(generated_text)} characters from Gemini")
                                return generated_text
                            else:
                                logger.error(f"Unexpected choice format: {choice}")
                                return f"Error: Unexpected response format in choices"
                        else:
                            logger.error(f"Unexpected response format from Gemini: {result}")
                            return "Error: Unexpected response format"
                    
                    except Exception as e:
                        logger.error(f"Error parsing Gemini response: {e}")
                        return f"Error parsing response: {e}"
                        
                except httpx.TimeoutException:
                    logger.error("Connection to Gemini API timed out")
                    return "Error: Connection to Gemini API timed out"
                
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
            sources_info = ""
            for idx, source in enumerate(research_data.get('sources', [])[:5]):
                sources_info += f"Source {idx+1}: {source.get('title', 'Unknown')} - {source.get('summary', '')[:300]}...\n\n"
            
            key_concepts = ", ".join(research_data.get('key_concepts', [])[:8])
            related_topics = ", ".join(research_data.get('related_topics', []))
            
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
  "recommendations": "Additional personalized recommendations based on learning style"
}}

Return ONLY the valid JSON object, nothing else. Ensure all JSON is properly formatted and valid.
"""
            result = await self.generate_content(prompt)
            
            try:
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
    
    def _generate_fallback_plan(self, topic: str, duration_weeks: int, is_disabled: bool = False) -> Dict[str, Any]:
        """
        Generate a fallback study plan when AI generation fails
        """
        if is_disabled:
            logger.warning(f"PLACEHOLDER MODE: Gemini generation disabled by configuration for topic: {topic}")
        else:
            logger.warning(f"FALLBACK MODE: Gemini generation failed, using template for topic: {topic}")
        
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
