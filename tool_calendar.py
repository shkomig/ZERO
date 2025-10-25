"""
Google Calendar Tool for Zero Agent
====================================
View, create, and manage calendar events

Requires:
    pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pytz

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False
    print("⚠️  Calendar libraries not installed. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


class CalendarTool:
    """
    Google Calendar integration for Zero Agent
    """
    
    # Calendar API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, credentials_path: Path = Path("credentials.json")):
        """
        Initialize Calendar tool
        
        Args:
            credentials_path: Path to Google OAuth credentials JSON
        """
        if not CALENDAR_AVAILABLE:
            raise ImportError("Calendar libraries not installed")
        
        self.credentials_path = credentials_path
        self.token_path = Path("calendar_token.pickle")
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Authenticate with Calendar API
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Refresh or get new token
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_path}\n"
                        "Download from: https://console.cloud.google.com/apis/credentials"
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), 
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_upcoming_events(self, 
                           days: int = 7,
                           max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get upcoming events
        
        Args:
            days: Number of days to look ahead
            max_results: Maximum number of events
            
        Returns:
            List of events
        """
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            end_time = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                timeMax=end_time,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                formatted_events.append(self._format_event(event))
            
            return formatted_events
            
        except Exception as e:
            print(f"Error getting events: {str(e)}")
            return []
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """
        Get today's events
        """
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=today_start.isoformat() + 'Z',
                timeMax=today_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            return [self._format_event(event) for event in events]
            
        except Exception as e:
            print(f"Error getting today's events: {str(e)}")
            return []
    
    def _format_event(self, event: Dict) -> Dict[str, Any]:
        """
        Format event for display
        """
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        return {
            'id': event['id'],
            'summary': event.get('summary', 'No Title'),
            'description': event.get('description', ''),
            'start': start,
            'end': end,
            'location': event.get('location', ''),
            'attendees': [a.get('email') for a in event.get('attendees', [])],
            'link': event.get('htmlLink', '')
        }
    
    def create_event(self,
                    summary: str,
                    start_time: datetime,
                    end_time: datetime,
                    description: str = "",
                    location: str = "",
                    attendees: Optional[List[str]] = None,
                    timezone: str = "UTC") -> Optional[str]:
        """
        Create calendar event
        
        Args:
            summary: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Event location
            attendees: List of attendee emails
            timezone: Timezone
            
        Returns:
            Event ID if successful
        """
        try:
            event = {
                'summary': summary,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
            }
            
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]
            
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event.get('id')
            
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return None
    
    def update_event(self,
                    event_id: str,
                    summary: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None,
                    description: Optional[str] = None) -> bool:
        """
        Update existing event
        """
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            # Update fields
            if summary:
                event['summary'] = summary
            if description:
                event['description'] = description
            if start_time:
                event['start']['dateTime'] = start_time.isoformat()
            if end_time:
                event['end']['dateTime'] = end_time.isoformat()
            
            # Update event
            self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event
            ).execute()
            
            return True
            
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return False
    
    def delete_event(self, event_id: str) -> bool:
        """
        Delete event
        """
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {str(e)}")
            return False
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search events by query
        """
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return [self._format_event(event) for event in events]
            
        except Exception as e:
            print(f"Error searching events: {str(e)}")
            return []
    
    def get_free_slots(self, 
                      date: datetime,
                      duration_minutes: int = 60,
                      start_hour: int = 9,
                      end_hour: int = 17) -> List[Dict[str, datetime]]:
        """
        Find free time slots on a given date
        
        Args:
            date: Date to check
            duration_minutes: Required slot duration
            start_hour: Start of work day
            end_hour: End of work day
            
        Returns:
            List of free slots
        """
        try:
            day_start = date.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            day_end = date.replace(hour=end_hour, minute=0, second=0, microsecond=0)
            
            # Get events for the day
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=day_start.isoformat() + 'Z',
                timeMax=day_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Find gaps
            free_slots = []
            current_time = day_start
            
            for event in events:
                event_start = datetime.fromisoformat(
                    event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00')
                )
                
                # Check if there's a gap
                if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                    free_slots.append({
                        'start': current_time,
                        'end': event_start
                    })
                
                event_end = datetime.fromisoformat(
                    event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00')
                )
                current_time = max(current_time, event_end)
            
            # Check remaining time
            if (day_end - current_time).total_seconds() >= duration_minutes * 60:
                free_slots.append({
                    'start': current_time,
                    'end': day_end
                })
            
            return free_slots
            
        except Exception as e:
            print(f"Error finding free slots: {str(e)}")
            return []


# Convenience functions for Zero Agent

def calendar_today() -> str:
    """
    Get today's events (for Zero Agent)
    """
    try:
        tool = CalendarTool()
        events = tool.get_today_events()
        
        if not events:
            return "No events today"
        
        result = f"Today's schedule ({len(events)} events):\n\n"
        for i, event in enumerate(events, 1):
            start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            result += f"{i}. {start_time.strftime('%H:%M')} - {event['summary']}\n"
            if event['location']:
                result += f"   📍 {event['location']}\n"
            if event['description']:
                result += f"   📝 {event['description'][:100]}\n"
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"


def calendar_week() -> str:
    """
    Get this week's events (for Zero Agent)
    """
    try:
        tool = CalendarTool()
        events = tool.get_upcoming_events(days=7)
        
        if not events:
            return "No events this week"
        
        result = f"This week's schedule ({len(events)} events):\n\n"
        for i, event in enumerate(events, 1):
            start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
            result += f"{i}. {start_time.strftime('%a %d/%m %H:%M')} - {event['summary']}\n"
        
        return result
        
    except Exception as e:
        return f"Error: {str(e)}"


def calendar_create(summary: str, start: str, end: str, description: str = "") -> str:
    """
    Create event (for Zero Agent)
    
    Args:
        summary: Event title
        start: Start time (ISO format or "2025-10-24 14:00")
        end: End time
        description: Event description
    """
    try:
        tool = CalendarTool()
        
        # Parse times
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
        
        event_id = tool.create_event(
            summary=summary,
            start_time=start_dt,
            end_time=end_dt,
            description=description
        )
        
        return f"✓ Event created: {summary}" if event_id else "✗ Failed to create event"
        
    except Exception as e:
        return f"Error: {str(e)}"


# Test
if __name__ == "__main__":
    if not CALENDAR_AVAILABLE:
        print("Install required libraries first:")
        print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    else:
        print("Calendar Tool Test")
        print("="*70)
        
        try:
            tool = CalendarTool()
            print("✓ Authenticated with Google Calendar")
            
            # Get today's events
            print("\n📅 Today's events:")
            events = tool.get_today_events()
            if events:
                for i, event in enumerate(events, 1):
                    print(f"\n{i}. {event['summary']}")
                    print(f"   Time: {event['start']}")
                    if event['location']:
                        print(f"   Location: {event['location']}")
            else:
                print("   No events today")
            
            # Get upcoming
            print("\n📆 Upcoming events (7 days):")
            upcoming = tool.get_upcoming_events(days=7, max_results=5)
            for i, event in enumerate(upcoming, 1):
                start_time = datetime.fromisoformat(event['start'].replace('Z', '+00:00'))
                print(f"{i}. {start_time.strftime('%a %d/%m %H:%M')} - {event['summary']}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
