
from pydantic import BaseModel
from typing import List, Optional

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

class IcsRequest(BaseModel):
    topic: str
    milestones: List[MilestoneItem]
