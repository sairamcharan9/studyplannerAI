from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import Response
from typing import List
from app.services.calendar_service import CalendarService
from app.models.plan import StudyPlanRequest, StudyPlanResponse, IcsRequest
from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService

# Create router
router = APIRouter(tags=["studyplanner"])

# Dependencies
def get_research_service():
    return ResearchService()

def get_study_plan_service():
    return StudyPlanService()

# Routes
@router.post("/generate-study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    research_service: ResearchService = Depends(get_research_service),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
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
            generate_goals=request.generate_goals,
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

@router.get("/suggestions", response_model=List[str])
async def get_suggestions(query: str = Query(..., min_length=3)):
    """
    Provide suggestions for study topics based on the user's query.
    """
    # In a real application, this could be a more sophisticated suggestion engine
    # (e.g., using a database, search index, or another AI model).
    predefined_suggestions = [
        "Machine Learning", "Web Development", "Python Programming", "Data Science",
        "Artificial Intelligence", "Cybersecurity", "Cloud Computing", "DevOps",
        "JavaScript", "React", "Node.js", "SQL", "NoSQL", "Blockchain",
        "Mobile App Development", "Game Development", "UI/UX Design"
    ]

    # Filter suggestions based on the query
    matching_suggestions = [s for s in predefined_suggestions if query.lower() in s.lower()]

    return matching_suggestions[:5]  # Return top 5 matches

@router.post("/generate-ics")
async def generate_ics(request: IcsRequest):
    """
    Generate an ICS file for the study plan.
    """
    try:
        calendar_service = CalendarService()
        ics_content = calendar_service.create_ics_file(request.topic, request.milestones)
        return Response(content=ics_content, media_type="text/calendar")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ICS file: {str(e)}")
