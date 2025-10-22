import os
import datetime
import pickle
import logging

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class CalendarService:
    def __init__(self):
        self.credentials = self._get_credentials()
        self.service = self._get_calendar_service()
        logger.info("Calendar service initialized")

    def _get_credentials(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # This part would typically be handled by a web flow in a FastAPI app
                # For local development, you might need a `credentials.json` file.
                # In a deployed app, you'd use a more robust OAuth2 flow.
                logger.warning("No valid Google Calendar credentials found. Please ensure 'client_secret.json' or 'credentials.json' is available and configured for OAuth2 flow.")
                # Placeholder for a non-interactive flow, if applicable, or raise error
                return None # Or raise an exception, depending on desired behavior
        
            # Save the credentials for the next run
            if creds and creds.valid:
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
        return creds

    def _get_calendar_service(self):
        if not self.credentials:
            logger.error("Google Calendar credentials not available. Cannot initialize service.")
            return None
        try:
            service = build('calendar', 'v3', credentials=self.credentials)
            return service
        except Exception as e:
            logger.error(f"Error building Google Calendar service: {e}")
            return None

    def create_calendar_event(self,
                              study_plan: Dict[str, Any],
                              calendar_id: str = 'primary') -> Optional[Dict[str, Any]]:
        if not self.service:
            logger.error("Google Calendar service not initialized. Cannot create event.")
            return None

        events = []
        for milestone in study_plan.get('milestones', []):
            week_number = milestone.get('week')
            estimated_hours = milestone.get('estimated_hours', 0)
            
            # Assuming a simple mapping for now: each milestone is a week-long event
            # In a real app, you'd want more granular control over dates and times
            # For demonstration, let's assume the study plan starts from today
            start_date = datetime.date.today() + datetime.timedelta(weeks=week_number - 1)
            end_date = start_date + datetime.timedelta(days=7) # A week-long event

            event = {
                'summary': f"{study_plan['topic']} - {milestone['title']}",
                'description': f"Learning Objectives: {', '.join(study_plan.get('learning_objectives', []))}\n\n"
                               f"Key Concepts: {', '.join(study_plan.get('key_concepts', []))}\n\n"
                               f"Tasks: {'; '.join(milestone.get('tasks', []))}\n\n"
                               f"Estimated Hours: {estimated_hours}",
                'start': {
                    'date': start_date.isoformat(),
                },
                'end': {
                    'date': end_date.isoformat(),
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            events.append(event)
        
        created_events_info = []
        for event in events:
            try:
                event = self.service.events().insert(calendarId=calendar_id, body=event).execute()
                logger.info(f"Event created: {event.get('htmlLink')}")
                created_events_info.append({
                    'summary': event.get('summary'),
                    'htmlLink': event.get('htmlLink'),
                    'id': event.get('id')
                })
            except Exception as e:
                logger.error(f"Error creating calendar event for {event.get('summary')}: {e}")
                created_events_info.append({
                    'summary': event.get('summary'),
                    'error': str(e)
                })
        
        return {"created_events": created_events_info}

def get_calendar_service():
    return CalendarService()
