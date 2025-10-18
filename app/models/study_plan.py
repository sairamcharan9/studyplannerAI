from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class StudyPlanRequest(BaseModel):
    topic: str
    depth_level: int = 3
    duration_weeks: int = 4
    include_resources: bool = True
    learning_style: Optional[str] = None
    prior_knowledge: Optional[str] = None
    goals: Optional[List[str]] = None
    additional_context: Optional[str] = None
    language: Optional[str] = "en"

class ResourceItem(BaseModel):
    title: str
    url: Optional[str] = None
    type: str
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
    prerequisites: Optional[List[str]] = None
    quiz: Optional[List[Dict[str, Any]]] = None
