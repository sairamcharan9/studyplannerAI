from fastapi import APIRouter, HTTPException, Depends, Query, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from app.services.research_service import ResearchService
from app.services.study_plan_service import StudyPlanService
from app.services.ai_service_factory import get_ai_service
from app.services.auth_service import AuthService, get_auth_service # New import for authentication
from app.services.calendar_service import CalendarService, get_calendar_service

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="templates")

# Create router
router = APIRouter(tags=["studyplanner"])

# Login/Logout Routes
@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...), auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error_message": "Invalid credentials"})
    
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session_token", value=user.username)
    return response

@router.get("/logout")
async def logout(response: RedirectResponse = RedirectResponse(url="/", status_code=302)):
    response.delete_cookie("session_token")
    return response

# Pydantic models for request/response
class StudyPlanRequest(BaseModel):
    topic: str
    depth_level: int = 3  # 1-5, where 5 is most detailed
    duration_weeks: int = 4
    include_resources: bool = True
    learning_style: Optional[str] = None  # visual, auditory, reading/writing, kinesthetic
    prior_knowledge: Optional[str] = None  # none, beginner, intermediate, advanced
    goals: Optional[List[str]] = None
    generate_goals: bool = False
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
    calendar_events_info: Optional[Dict[str, Any]] = None

# Dependencies
def get_research_service():
    return ResearchService()

def get_study_plan_service():
    return StudyPlanService()

def get_calendar_service_dependency():
    return CalendarService()

# Routes
@router.post("/generate-study-plan", response_model=StudyPlanResponse)
async def generate_study_plan(
    request: StudyPlanRequest,
    research_service: ResearchService = Depends(get_research_service),
    study_plan_service: StudyPlanService = Depends(get_study_plan_service),
    ai_service = Depends(get_ai_service),
    calendar_service: CalendarService = Depends(get_calendar_service_dependency),
):
    """
    Generate a study plan based on research and user requirements.
    """
    try:
        # 1. Research the topic
        research_results = await research_service.research_topic(request.topic)
        
        # 2. Generate the study plan using the selected AI service
        study_plan = await study_plan_service.generate_plan(
            ai_service=ai_service,
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

        # 3. Add study plan to calendar
        calendar_events_info = calendar_service.create_calendar_event(study_plan)
        if calendar_events_info:
            study_plan["calendar_events_info"] = calendar_events_info
        
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