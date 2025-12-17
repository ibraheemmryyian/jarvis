"""
Calendar Agent for Jarvis v2
Google Calendar integration for scheduling and event management.
"""
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from .config import WORKSPACE_DIR

# Optional: Google Calendar API
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


class CalendarAgent:
    """
    Calendar management agent.
    
    Features:
    - Google Calendar OAuth integration
    - View upcoming events
    - Create events
    - Find free time slots
    - Meeting scheduling
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.credentials_path = os.path.join(WORKSPACE_DIR, "credentials")
        os.makedirs(self.credentials_path, exist_ok=True)
        
        self._load_credentials()
    
    def _load_credentials(self):
        """Load Calendar credentials if available."""
        if not CALENDAR_AVAILABLE:
            print("[CalendarAgent] Google Calendar API libraries not installed")
            return
        
        token_path = os.path.join(self.credentials_path, "calendar_token.json")
        
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        
        if self.creds and self.creds.expired and self.creds.refresh_token:
            try:
                self.creds.refresh(Request())
                self._save_credentials()
            except Exception as e:
                print(f"[CalendarAgent] Token refresh failed: {e}")
                self.creds = None
        
        if self.creds and self.creds.valid:
            try:
                self.service = build('calendar', 'v3', credentials=self.creds)
                print("[CalendarAgent] Google Calendar connected")
            except Exception as e:
                print(f"[CalendarAgent] Service build failed: {e}")
    
    def _save_credentials(self):
        """Save credentials to file."""
        token_path = os.path.join(self.credentials_path, "calendar_token.json")
        with open(token_path, 'w') as f:
            f.write(self.creds.to_json())
    
    def authenticate(self, credentials_file: str = None) -> Dict:
        """Authenticate with Google Calendar OAuth."""
        if not CALENDAR_AVAILABLE:
            return {"success": False, "error": "Google Calendar API libraries not installed"}
        
        creds_file = credentials_file or os.path.join(
            self.credentials_path, "calendar_credentials.json"
        )
        
        if not os.path.exists(creds_file):
            return {
                "success": False,
                "error": f"Credentials file not found: {creds_file}"
            }
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(creds_file, self.SCOPES)
            self.creds = flow.run_local_server(port=0)
            self._save_credentials()
            self.service = build('calendar', 'v3', credentials=self.creds)
            
            return {"success": True, "message": "Calendar authenticated"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_connected(self) -> bool:
        """Check if Calendar is connected."""
        return self.service is not None
    
    def get_upcoming(self, days: int = 7, max_results: int = 20) -> List[Dict]:
        """Get upcoming events."""
        if not self.is_connected():
            return self.mock_events()  # Return mock data if not connected
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [
                {
                    "id": event.get('id'),
                    "title": event.get('summary', 'No title'),
                    "start": event['start'].get('dateTime', event['start'].get('date')),
                    "end": event['end'].get('dateTime', event['end'].get('date')),
                    "location": event.get('location', ''),
                    "description": event.get('description', '')[:200],
                    "attendees": [a.get('email') for a in event.get('attendees', [])]
                }
                for event in events
            ]
        except Exception as e:
            return [{"error": str(e)}]
    
    def create_event(self, title: str, start: str, end: str,
                     description: str = "", location: str = "",
                     attendees: List[str] = None) -> Dict:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start: Start time (ISO format)
            end: End time (ISO format)
            description: Event description
            location: Event location
            attendees: List of email addresses
        """
        if not self.is_connected():
            return {"success": False, "error": "Calendar not connected"}
        
        try:
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {'dateTime': start, 'timeZone': 'UTC'},
                'end': {'dateTime': end, 'timeZone': 'UTC'},
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            result = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all' if attendees else 'none'
            ).execute()
            
            return {
                "success": True,
                "event_id": result.get('id'),
                "link": result.get('htmlLink')
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_free_slots(self, duration_minutes: int = 30, 
                        days_ahead: int = 7) -> List[Dict]:
        """Find free time slots for scheduling."""
        if not self.is_connected():
            # Return mock free slots
            now = datetime.now()
            slots = []
            for i in range(1, 6):
                slot_start = now + timedelta(days=i, hours=10)
                slot_end = slot_start + timedelta(minutes=duration_minutes)
                slots.append({
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat(),
                    "duration_minutes": duration_minutes
                })
            return slots
        
        try:
            events = self.get_upcoming(days=days_ahead, max_results=50)
            
            # Simple free slot finder - gaps between events
            free_slots = []
            now = datetime.utcnow()
            
            # Work hours: 9 AM to 6 PM
            for day_offset in range(days_ahead):
                day = now + timedelta(days=day_offset)
                day_start = day.replace(hour=9, minute=0, second=0, microsecond=0)
                day_end = day.replace(hour=18, minute=0, second=0, microsecond=0)
                
                # Skip past times
                if day_start < now:
                    day_start = now
                
                # Check for conflicts
                day_events = [e for e in events if 'start' in e and day.date().isoformat() in e['start']]
                
                if not day_events:
                    # Whole day is free
                    free_slots.append({
                        "start": day_start.isoformat(),
                        "end": day_end.isoformat(),
                        "duration_minutes": (day_end - day_start).seconds // 60
                    })
            
            return free_slots[:10]
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_today_summary(self) -> str:
        """Get a summary of today's events."""
        events = self.get_upcoming(days=1, max_results=10)
        
        if not events:
            return "No events scheduled for today."
        
        if len(events) == 1 and "error" in events[0]:
            return "Unable to fetch calendar. May not be connected."
        
        summary = f"## Today's Schedule ({len(events)} events)\n\n"
        
        for event in events:
            time_str = event.get('start', 'TBD')
            if 'T' in time_str:
                time_str = time_str.split('T')[1][:5]  # Get HH:MM
            
            summary += f"- **{time_str}** - {event.get('title', 'No title')}\n"
            if event.get('location'):
                summary += f"  📍 {event['location']}\n"
        
        return summary
    
    def mock_events(self) -> List[Dict]:
        """Return mock events for testing without Calendar connection."""
        now = datetime.now()
        return [
            {
                "id": "mock_1",
                "title": "Product Review Meeting",
                "start": (now + timedelta(hours=2)).isoformat(),
                "end": (now + timedelta(hours=3)).isoformat(),
                "location": "Zoom",
                "attendees": ["team@company.com"]
            },
            {
                "id": "mock_2",
                "title": "Investor Call",
                "start": (now + timedelta(days=1, hours=10)).isoformat(),
                "end": (now + timedelta(days=1, hours=11)).isoformat(),
                "location": "Google Meet",
                "attendees": ["investor@vc.com"]
            },
            {
                "id": "mock_3",
                "title": "Weekly Standup",
                "start": (now + timedelta(days=2, hours=9)).isoformat(),
                "end": (now + timedelta(days=2, hours=9, minutes=30)).isoformat(),
                "location": "",
                "attendees": []
            }
        ]


# Singleton
calendar_agent = CalendarAgent()
