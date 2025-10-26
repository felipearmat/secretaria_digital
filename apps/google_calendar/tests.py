from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from apps.google_calendar.models import (
    GoogleCalendarIntegration, 
    GoogleCalendarEvent, 
    GoogleCalendarSyncLog
)
from apps.google_calendar.services import GoogleCalendarService, GoogleCalendarOAuthService
from apps.appointments.models import Appointment, Service
from apps.companies.models import Company

User = get_user_model()


class GoogleCalendarIntegrationModelTest(TestCase):
    """Tests for GoogleCalendarIntegration model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            user=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            calendar_id="primary",
            sync_enabled=True,
            sync_direction="bidirectional"
        )
    
    def test_integration_creation(self):
        """Tests integration creation."""
        self.assertEqual(self.integration.user, self.user)
        self.assertEqual(self.integration.calendar_id, "primary")
        self.assertTrue(self.integration.sync_enabled)
        self.assertEqual(self.integration.sync_direction, "bidirectional")
    
    def test_is_token_expired(self):
        """Tests expired token verification."""
        # Valid token
        self.assertFalse(self.integration.is_token_expired)
        
        # Expired token
        self.integration.token_expires_at = timezone.now() - timedelta(hours=1)
        self.assertTrue(self.integration.is_token_expired)
    
    def test_needs_refresh(self):
        """Tests token renewal necessity verification."""
        # Valid token
        self.assertFalse(self.integration.needs_refresh())
        
        # Token expires in 3 minutes (less than 5)
        self.integration.token_expires_at = timezone.now() + timedelta(minutes=3)
        self.assertTrue(self.integration.needs_refresh())


class GoogleCalendarEventModelTest(TestCase):
    """Tests for GoogleCalendarEvent model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            description="Service description",
            duration_minutes=60,
            base_price=100.00,
            company=self.company,
            actor=self.user
        )
        
        self.appointment = Appointment.objects.create(
            client=self.user,
            actor=self.user,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            status="confirmed"
        )
        
        self.google_event = GoogleCalendarEvent.objects.create(
            appointment=self.appointment,
            google_event_id="google_event_123",
            google_calendar_id="primary",
            sync_status="synced"
        )
    
    def test_google_event_creation(self):
        """Tests Google Calendar event creation."""
        self.assertEqual(self.google_event.appointment, self.appointment)
        self.assertEqual(self.google_event.google_event_id, "google_event_123")
        self.assertEqual(self.google_event.sync_status, "synced")
    
    def test_unique_constraint(self):
        """Tests unique constraint for google_event_id and google_calendar_id."""
        with self.assertRaises(Exception):
            GoogleCalendarEvent.objects.create(
                appointment=self.appointment,
                google_event_id="google_event_123",
                google_calendar_id="primary",
                sync_status="synced"
            )


class GoogleCalendarSyncLogModelTest(TestCase):
    """Tests for GoogleCalendarSyncLog model."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            user=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1)
        )
        
        self.sync_log = GoogleCalendarSyncLog.objects.create(
            integration=self.integration,
            sync_type="manual",
            events_created=5,
            events_updated=3,
            events_deleted=1,
            status="success",
            started_at=timezone.now(),
            completed_at=timezone.now() + timedelta(seconds=30)
        )
    
    def test_sync_log_creation(self):
        """Tests sync log creation."""
        self.assertEqual(self.sync_log.integration, self.integration)
        self.assertEqual(self.sync_log.sync_type, "manual")
        self.assertEqual(self.sync_log.events_created, 5)
        self.assertEqual(self.sync_log.status, "success")
    
    def test_duration_calculation(self):
        """Tests duration calculation."""
        self.assertEqual(self.sync_log.duration_seconds, 30)


class GoogleCalendarServiceTest(TestCase):
    """Tests for GoogleCalendarService."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            user=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            calendar_id="primary"
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            description="Service description",
            duration_minutes=60,
            base_price=100.00,
            company=self.company,
            actor=self.user
        )
        
        self.appointment = Appointment.objects.create(
            client=self.user,
            actor=self.user,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            status="confirmed"
        )
    
    @patch('apps.google_calendar.services.build')
    def test_service_creation(self, mock_build):
        """Tests service creation."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        
        self.assertIsNotNone(service.service)
        mock_build.assert_called_once()
    
    @patch('apps.google_calendar.services.build')
    def test_prepare_event_data(self, mock_build):
        """Tests event data preparation."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        event_data = service._prepare_event_data(self.appointment)
        
        self.assertIn('summary', event_data)
        self.assertIn('description', event_data)
        self.assertIn('start', event_data)
        self.assertIn('end', event_data)
        self.assertIn('attendees', event_data)
        self.assertIn('reminders', event_data)
        self.assertIn('extendedProperties', event_data)
    
    @patch('apps.google_calendar.services.build')
    def test_create_event(self, mock_build):
        """Tests Google Calendar event creation."""
        mock_service = MagicMock()
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'id': 'google_event_123'
        }
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        google_event = service.create_event(self.appointment)
        
        self.assertIsInstance(google_event, GoogleCalendarEvent)
        self.assertEqual(google_event.google_event_id, 'google_event_123')
        self.assertEqual(google_event.sync_status, 'synced')


class GoogleCalendarOAuthServiceTest(TestCase):
    """Tests for GoogleCalendarOAuthService."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
    
    @patch('apps.google_calendar.services.Flow.from_client_config')
    def test_get_authorization_url(self, mock_flow):
        """Tests authorization URL generation."""
        mock_flow_instance = MagicMock()
        mock_flow_instance.authorization_url.return_value = (
            'https://accounts.google.com/oauth2/auth?client_id=test',
            'state_123'
        )
        mock_flow.return_value = mock_flow_instance
        
        url = GoogleCalendarOAuthService.get_authorization_url(self.user)
        
        self.assertIn('accounts.google.com', url)
        mock_flow_instance.authorization_url.assert_called_once()
    
    @patch('apps.google_calendar.services.Flow.from_client_config')
    def test_handle_authorization_callback(self, mock_flow):
        """Testa processamento de callback OAuth."""
        mock_flow_instance = MagicMock()
        mock_credentials = MagicMock()
        mock_credentials.token = 'new_access_token'
        mock_credentials.refresh_token = 'new_refresh_token'
        mock_credentials.expiry = 3600
        mock_flow_instance.fetch_token.return_value = None
        mock_flow_instance.credentials = mock_credentials
        mock_flow.return_value = mock_flow_instance
        
        integration = GoogleCalendarOAuthService.handle_authorization_callback(
            self.user, 'http://localhost:8000/callback/?code=test_code'
        )
        
        self.assertIsInstance(integration, GoogleCalendarIntegration)
        self.assertEqual(integration.user, self.user)
        self.assertEqual(integration.access_token, 'new_access_token')


class GoogleCalendarTasksTest(TestCase):
    """Tests for Celery tasks."""
    
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            company=self.company
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            user=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            sync_enabled=True
        )
        
        self.service = Service.objects.create(
            name="Test Service",
            description="Service description",
            duration_minutes=60,
            base_price=100.00,
            company=self.company,
            actor=self.user
        )
        
        self.appointment = Appointment.objects.create(
            client=self.user,
            actor=self.user,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            status="confirmed"
        )
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_sync_appointment_to_google_calendar(self, mock_service_class):
        """Tests appointment synchronization to Google Calendar."""
        mock_service = MagicMock()
        mock_google_event = MagicMock()
        mock_service.create_event.return_value = mock_google_event
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import sync_appointment_to_google_calendar
        
        # Execute the task
        sync_appointment_to_google_calendar(self.appointment.id)
        
        # Verify if the service was called
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.create_event.assert_called_once_with(self.appointment)
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_remove_appointment_from_google_calendar(self, mock_service_class):
        """Tests appointment removal from Google Calendar."""
        # Create mapped event
        google_event = GoogleCalendarEvent.objects.create(
            appointment=self.appointment,
            google_event_id="google_event_123",
            google_calendar_id="primary"
        )
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import remove_appointment_from_google_calendar
        
        # Execute the task
        remove_appointment_from_google_calendar(self.appointment.id)
        
        # Verify if the service was called
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.delete_event.assert_called_once_with(google_event)
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_sync_from_google_calendar(self, mock_service_class):
        """Tests Google Calendar synchronization to the system."""
        mock_service = MagicMock()
        mock_service.sync_from_google.return_value = {
            'events_processed': 10,
            'events_created': 5,
            'events_updated': 3,
            'events_conflicted': 2
        }
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import sync_from_google_calendar
        
        # Execute the task
        result = sync_from_google_calendar(self.integration.id)
        
        # Verify if the service was called
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.sync_from_google.assert_called_once()
        
        # Verify if the log was created
        sync_log = GoogleCalendarSyncLog.objects.filter(
            integration=self.integration
        ).first()
        self.assertIsNotNone(sync_log)
        self.assertEqual(sync_log.status, 'success')

