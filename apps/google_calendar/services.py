"""
Google Calendar integration services.
"""

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import GoogleCalendarEvent, GoogleCalendarSyncLog, GoogleCalendarIntegration


class GoogleCalendarService:
    """Service class for Google Calendar operations."""
    
    def __init__(self, integration):
        """Initialize the service with an integration object."""
        self.integration = integration
        self.service = self._build_service()
    
    def _build_service(self):
        """Build the Google Calendar API service."""
        credentials = Credentials(
            token=self.integration.access_token,
            refresh_token=self.integration.refresh_token,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self.integration.client_id,
            client_secret=self.integration.client_secret
        )
        return build('calendar', 'v3', credentials=credentials)
    
    def create_event(self, appointment):
        """Create a new event in Google Calendar."""
        event = {
            'summary': f'Appointment: {appointment.service.name}',
            'description': f'Client: {appointment.client.get_full_name() if hasattr(appointment.client, "get_full_name") else appointment.client.username}',
            'start': {
                'dateTime': appointment.start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': appointment.end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            # Create GoogleCalendarEvent record
            google_event = GoogleCalendarEvent.objects.create(
                appointment=appointment,
                google_event_id=created_event['id'],
                google_calendar_id='primary',
                sync_status='synced'
            )
            
            self._log_sync('create', appointment.id, 'success')
            return google_event
            
        except Exception as e:
            self._log_sync('create', appointment.id, 'error', str(e))
            raise
    
    def update_event(self, google_event):
        """Update an existing event in Google Calendar."""
        appointment = google_event.appointment
        
        event = {
            'summary': f'Appointment: {appointment.service.name}',
            'description': f'Client: {appointment.client.get_full_name() if hasattr(appointment.client, "get_full_name") else appointment.client.username}',
            'start': {
                'dateTime': appointment.start_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': appointment.end_time.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }
        
        try:
            self.service.events().update(
                calendarId=google_event.google_calendar_id,
                eventId=google_event.google_event_id,
                body=event
            ).execute()
            
            google_event.sync_status = 'synced'
            google_event.sync_error = None
            google_event.last_sync_at = timezone.now()
            google_event.save()
            
            self._log_sync('update', appointment.id, 'success')
            
        except Exception as e:
            google_event.sync_status = 'error'
            google_event.sync_error = str(e)
            google_event.save()
            
            self._log_sync('update', appointment.id, 'error', str(e))
            raise
    
    def delete_event(self, google_event):
        """Delete an event from Google Calendar."""
        try:
            self.service.events().delete(
                calendarId=google_event.google_calendar_id,
                eventId=google_event.google_event_id
            ).execute()
            
            self._log_sync('delete', google_event.appointment.id, 'success')
            google_event.delete()
            
        except Exception as e:
            self._log_sync('delete', google_event.appointment.id, 'error', str(e))
            raise
    
    def _log_sync(self, operation, appointment_id, status, error_message=None):
        """Log synchronization operation."""
        GoogleCalendarSyncLog.objects.create(
            integration=self.integration,
            operation=operation,
            appointment_id=appointment_id,
            status=status,
            error_message=error_message
        )


class GoogleCalendarOAuthService:
    """Service class for Google Calendar OAuth operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    @classmethod
    def get_authorization_url(cls, redirect_uri):
        """Generate OAuth authorization URL."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=cls.SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        return authorization_url, state
    
    @classmethod
    def exchange_code(cls, code, redirect_uri):
        """Exchange authorization code for tokens."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=cls.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_expiry': credentials.expiry
        }

