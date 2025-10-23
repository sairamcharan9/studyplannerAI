
from ics import Calendar, Event
from datetime import datetime, timedelta
from typing import List
from app.models.plan import MilestoneItem

class CalendarService:
    def create_ics_file(self, topic: str, milestones: List[MilestoneItem]) -> str:
        c = Calendar()
        start_date = datetime.now()
        for milestone in milestones:
            e = Event()
            e.name = f"{topic}: {milestone.title}"
            e.begin = start_date + timedelta(weeks=milestone.week - 1)
            e.end = e.begin + timedelta(hours=milestone.estimated_hours)
            e.description = milestone.description
            c.events.add(e)
        return str(c)
