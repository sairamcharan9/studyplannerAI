from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ollama_service import OllamaService

# Create router
router = APIRouter(tags=["studyplanner"])

# Pydantic models for request/response
class StudyPlanRequest(BaseModel):
    topic: str
    depth_level: int = 3  # 1-5, where 5 is most detailed
    duration_weeks: int = 4
    include_resources: bool = True
    learning_style: Optional[str] = None  # visual, auditory, reading/writing, kinesthetic
    prior_knowledge: Optional[str] = None  # none, beginner, intermediate, advanced
    goals: Optional[List[str]] = None
    additional_context: Optional[str] = None

class ResourceItem(BaseModel):
    title: str
    url: Optional[str] = None
    type: str  # book, article, video, course, etc.
    description: Optional[str] = None

class MilestoneItem(BaseModel):
    title: str
    description: str
    week: int
    tasks: List[str]
    estimated_hours: int

class StudyPlanResponse(BaseModel):
    topic: str
    summary: str
    duration_weeks: int
    learning_objectives: List[str]
    key_concepts: List[str]
    milestones: List[MilestoneItem]
    resources: Optional[List[ResourceItem]] = None
    recommendations: Optional[str] = None

# Dependencies
def get_research_service():
    return ResearchService()

def get_study_plan_service():
    return StudyPlanService()

def get_ollama_service():
    return OllamaService()

# Routes
@router.post("/generate-study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    research_service: ResearchService = Depends(get_research_service),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
    ollama_service: OllamaService = Depends(get_ollama_service),
):
    """
    Generate a study plan based on research and user requirements.
    """
    try:
        # 1. Research the topic
        research_results = await research_service.research_topic(request.topic)
        
        # 2. Generate the study plan using Ollama
        study_plan = await study_plan_service.generate_plan(
            topic=request.topic, 
            research_data=research_results,
            depth_level=request.depth_level,
            duration_weeks=request.duration_weeks,
            include_resources=request.include_resources,
            learning_style=request.learning_style,
            prior_knowledge=request.prior_knowledge,
            goals=request.goals,
            additional_context=request.additional_context
        )
        
        return study_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")

@router.get("/topics/trending", response_model=List[str])
async def get_trending_topics(
    research_service: ResearchService = Depends(get_research_service),
):
    """
    Get trending study topics.
    """
    try:
        trending_topics = await research_service.get_trending_topics()
        return trending_topics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")
