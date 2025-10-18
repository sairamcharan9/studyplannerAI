from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service import AIService
from app.models import (
    StudyPlanRequest,
    StudyPlanResponse,
    TranslationRequest,
    SummarizationRequest,
    KeywordRequest,
)

# Create router
router = APIRouter(tags=["studyplanner"])

# Dependencies
def get_research_service():
    return ResearchService()

def get_study_plan_service():
    return StudyPlanService()

def get_ai_service():
    return AIService()

# Routes
@router.post("/generate-study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    research_service: ResearchService = Depends(get_research_service),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Generate a study plan based on research and user requirements.
    """
    try:
        research_results = await research_service.research_topic(request.topic)
        
        study_plan = await study_plan_service.generate_plan(
            topic=request.topic, 
            research_data=research_results,
            ai_service=ai_service,
            depth_level=request.depth_level,
            duration_weeks=request.duration_weeks,
            include_resources=request.include_resources,
            learning_style=request.learning_style,
            prior_knowledge=request.prior_knowledge,
            goals=request.goals,
            additional_context=request.additional_context
        )
        
        if request.language != "en":
            study_plan["summary"] = await ai_service.translate_text(study_plan["summary"], request.language)

        return study_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")

@router.post("/translate")
async def translate_text(
    request: TranslationRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Translate text to a target language.
    """
    try:
        return await ai_service.translate_text(request.text, request.target_language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to translate text: {str(e)}")

@router.post("/summarize")
async def summarize_text(
    request: SummarizationRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Summarize a block of text.
    """
    try:
        return await ai_service.summarize_text(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to summarize text: {str(e)}")

@router.post("/extract-keywords")
async def extract_keywords(
    request: KeywordRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Extract keywords from a block of text.
    """
    try:
        return await ai_service.extract_keywords(request.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract keywords: {str(e)}")

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
