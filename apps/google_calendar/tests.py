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
from apps.agendamentos.models import Agendamento, Servico
from apps.empresas.models import Empresa

User = get_user_model()


class GoogleCalendarIntegrationModelTest(TestCase):
    """Testes para o modelo GoogleCalendarIntegration."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            usuario=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            calendar_id="primary",
            sync_enabled=True,
            sync_direction="bidirectional"
        )
    
    def test_integration_creation(self):
        """Testa criação de integração."""
        self.assertEqual(self.integration.usuario, self.user)
        self.assertEqual(self.integration.calendar_id, "primary")
        self.assertTrue(self.integration.sync_enabled)
        self.assertEqual(self.integration.sync_direction, "bidirectional")
    
    def test_is_token_expired(self):
        """Testa verificação de token expirado."""
        # Token válido
        self.assertFalse(self.integration.is_token_expired)
        
        # Token expirado
        self.integration.token_expires_at = timezone.now() - timedelta(hours=1)
        self.assertTrue(self.integration.is_token_expired)
    
    def test_needs_refresh(self):
        """Testa verificação de necessidade de renovação."""
        # Token válido
        self.assertFalse(self.integration.needs_refresh())
        
        # Token expira em 3 minutos (menos que 5)
        self.integration.token_expires_at = timezone.now() + timedelta(minutes=3)
        self.assertTrue(self.integration.needs_refresh())


class GoogleCalendarEventModelTest(TestCase):
    """Testes para o modelo GoogleCalendarEvent."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
        
        self.servico = Servico.objects.create(
            nome="Serviço Teste",
            descricao="Descrição do serviço",
            duracao_minutos=60,
            preco=100.00,
            empresa=self.empresa,
            ator=self.user
        )
        
        self.agendamento = Agendamento.objects.create(
            cliente=self.user,
            ator=self.user,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=2),
            status="confirmado"
        )
        
        self.google_event = GoogleCalendarEvent.objects.create(
            agendamento=self.agendamento,
            google_event_id="google_event_123",
            google_calendar_id="primary",
            sync_status="synced"
        )
    
    def test_google_event_creation(self):
        """Testa criação de evento Google Calendar."""
        self.assertEqual(self.google_event.agendamento, self.agendamento)
        self.assertEqual(self.google_event.google_event_id, "google_event_123")
        self.assertEqual(self.google_event.sync_status, "synced")
    
    def test_unique_constraint(self):
        """Testa constraint único de google_event_id e google_calendar_id."""
        with self.assertRaises(Exception):
            GoogleCalendarEvent.objects.create(
                agendamento=self.agendamento,
                google_event_id="google_event_123",
                google_calendar_id="primary",
                sync_status="synced"
            )


class GoogleCalendarSyncLogModelTest(TestCase):
    """Testes para o modelo GoogleCalendarSyncLog."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            usuario=self.user,
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
        """Testa criação de log de sincronização."""
        self.assertEqual(self.sync_log.integration, self.integration)
        self.assertEqual(self.sync_log.sync_type, "manual")
        self.assertEqual(self.sync_log.events_created, 5)
        self.assertEqual(self.sync_log.status, "success")
    
    def test_duration_calculation(self):
        """Testa cálculo de duração."""
        self.assertEqual(self.sync_log.duration_seconds, 30)


class GoogleCalendarServiceTest(TestCase):
    """Testes para o serviço GoogleCalendarService."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            usuario=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            calendar_id="primary"
        )
        
        self.servico = Servico.objects.create(
            nome="Serviço Teste",
            descricao="Descrição do serviço",
            duracao_minutos=60,
            preco=100.00,
            empresa=self.empresa,
            ator=self.user
        )
        
        self.agendamento = Agendamento.objects.create(
            cliente=self.user,
            ator=self.user,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=2),
            status="confirmado"
        )
    
    @patch('apps.google_calendar.services.build')
    def test_service_creation(self, mock_build):
        """Testa criação do serviço."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        
        self.assertIsNotNone(service.service)
        mock_build.assert_called_once()
    
    @patch('apps.google_calendar.services.build')
    def test_prepare_event_data(self, mock_build):
        """Testa preparação de dados do evento."""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        event_data = service._prepare_event_data(self.agendamento)
        
        self.assertIn('summary', event_data)
        self.assertIn('description', event_data)
        self.assertIn('start', event_data)
        self.assertIn('end', event_data)
        self.assertIn('attendees', event_data)
        self.assertIn('reminders', event_data)
        self.assertIn('extendedProperties', event_data)
    
    @patch('apps.google_calendar.services.build')
    def test_create_event(self, mock_build):
        """Testa criação de evento no Google Calendar."""
        mock_service = MagicMock()
        mock_service.events.return_value.insert.return_value.execute.return_value = {
            'id': 'google_event_123'
        }
        mock_build.return_value = mock_service
        
        service = GoogleCalendarService(self.integration)
        google_event = service.create_event(self.agendamento)
        
        self.assertIsInstance(google_event, GoogleCalendarEvent)
        self.assertEqual(google_event.google_event_id, 'google_event_123')
        self.assertEqual(google_event.sync_status, 'synced')


class GoogleCalendarOAuthServiceTest(TestCase):
    """Testes para o serviço GoogleCalendarOAuthService."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
    
    @patch('apps.google_calendar.services.Flow.from_client_config')
    def test_get_authorization_url(self, mock_flow):
        """Testa geração de URL de autorização."""
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
        self.assertEqual(integration.usuario, self.user)
        self.assertEqual(integration.access_token, 'new_access_token')


class GoogleCalendarTasksTest(TestCase):
    """Testes para as tasks do Celery."""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nome="Empresa Teste",
            cnpj="12345678000199"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            empresa=self.empresa
        )
        
        self.integration = GoogleCalendarIntegration.objects.create(
            usuario=self.user,
            access_token="test_access_token",
            refresh_token="test_refresh_token",
            token_expires_at=timezone.now() + timedelta(hours=1),
            sync_enabled=True
        )
        
        self.servico = Servico.objects.create(
            nome="Serviço Teste",
            descricao="Descrição do serviço",
            duracao_minutos=60,
            preco=100.00,
            empresa=self.empresa,
            ator=self.user
        )
        
        self.agendamento = Agendamento.objects.create(
            cliente=self.user,
            ator=self.user,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=2),
            status="confirmado"
        )
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_sync_agendamento_to_google_calendar(self, mock_service_class):
        """Testa sincronização de agendamento para Google Calendar."""
        mock_service = MagicMock()
        mock_google_event = MagicMock()
        mock_service.create_event.return_value = mock_google_event
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import sync_agendamento_to_google_calendar
        
        # Executa a task
        sync_agendamento_to_google_calendar(self.agendamento.id)
        
        # Verifica se o serviço foi chamado
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.create_event.assert_called_once_with(self.agendamento)
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_remove_agendamento_from_google_calendar(self, mock_service_class):
        """Testa remoção de agendamento do Google Calendar."""
        # Cria evento mapeado
        google_event = GoogleCalendarEvent.objects.create(
            agendamento=self.agendamento,
            google_event_id="google_event_123",
            google_calendar_id="primary"
        )
        
        mock_service = MagicMock()
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import remove_agendamento_from_google_calendar
        
        # Executa a task
        remove_agendamento_from_google_calendar(self.agendamento.id)
        
        # Verifica se o serviço foi chamado
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.delete_event.assert_called_once_with(google_event)
    
    @patch('apps.google_calendar.tasks.GoogleCalendarService')
    def test_sync_from_google_calendar(self, mock_service_class):
        """Testa sincronização do Google Calendar para o sistema."""
        mock_service = MagicMock()
        mock_service.sync_from_google.return_value = {
            'events_processed': 10,
            'events_created': 5,
            'events_updated': 3,
            'events_conflicted': 2
        }
        mock_service_class.return_value = mock_service
        
        from apps.google_calendar.tasks import sync_from_google_calendar
        
        # Executa a task
        result = sync_from_google_calendar(self.integration.id)
        
        # Verifica se o serviço foi chamado
        mock_service_class.assert_called_once_with(self.integration)
        mock_service.sync_from_google.assert_called_once()
        
        # Verifica se o log foi criado
        sync_log = GoogleCalendarSyncLog.objects.filter(
            integration=self.integration
        ).first()
        self.assertIsNotNone(sync_log)
        self.assertEqual(sync_log.status, 'success')

