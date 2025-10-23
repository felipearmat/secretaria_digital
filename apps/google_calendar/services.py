import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from django.conf import settings
from django.utils import timezone
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from apps.google_calendar.models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from apps.agendamentos.models import Agendamento
from apps.autenticacao.models import Usuario


class GoogleCalendarService:
    """
    Serviço para integração com Google Calendar API.
    """
    
    # Scopes necessários para acessar o Google Calendar
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self, integration: GoogleCalendarIntegration):
        self.integration = integration
        self.service = None
        self._build_service()
    
    def _build_service(self):
        """Constrói o serviço do Google Calendar API."""
        try:
            # Cria as credenciais
            credentials = Credentials(
                token=self.integration.access_token,
                refresh_token=self.integration.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET,
                scopes=self.SCOPES
            )
            
            # Renova o token se necessário
            if self.integration.needs_refresh():
                credentials.refresh(Request())
                self._update_tokens(credentials)
            
            # Constrói o serviço
            self.service = build('calendar', 'v3', credentials=credentials)
            
        except Exception as e:
            raise Exception(f"Erro ao construir serviço Google Calendar: {str(e)}")
    
    def _update_tokens(self, credentials: Credentials):
        """Atualiza os tokens no banco de dados."""
        self.integration.access_token = credentials.token
        if credentials.refresh_token:
            self.integration.refresh_token = credentials.refresh_token
        self.integration.token_expires_at = timezone.now() + timedelta(seconds=credentials.expiry)
        self.integration.save()
    
    def create_event(self, agendamento: Agendamento) -> GoogleCalendarEvent:
        """
        Cria um evento no Google Calendar baseado em um agendamento.
        """
        try:
            # Prepara os dados do evento
            event_data = self._prepare_event_data(agendamento)
            
            # Cria o evento no Google Calendar
            event = self.service.events().insert(
                calendarId=self.integration.calendar_id,
                body=event_data
            ).execute()
            
            # Salva o mapeamento no banco
            google_event = GoogleCalendarEvent.objects.create(
                agendamento=agendamento,
                google_event_id=event['id'],
                google_calendar_id=self.integration.calendar_id,
                sync_status='synced'
            )
            
            return google_event
            
        except HttpError as e:
            # Salva erro de sincronização
            google_event = GoogleCalendarEvent.objects.create(
                agendamento=agendamento,
                google_event_id='',
                google_calendar_id=self.integration.calendar_id,
                sync_status='error',
                sync_error=str(e)
            )
            raise Exception(f"Erro ao criar evento no Google Calendar: {str(e)}")
    
    def update_event(self, google_event: GoogleCalendarEvent) -> GoogleCalendarEvent:
        """
        Atualiza um evento no Google Calendar.
        """
        try:
            agendamento = google_event.agendamento
            
            # Prepara os dados atualizados do evento
            event_data = self._prepare_event_data(agendamento)
            
            # Atualiza o evento no Google Calendar
            updated_event = self.service.events().update(
                calendarId=self.integration.calendar_id,
                eventId=google_event.google_event_id,
                body=event_data
            ).execute()
            
            # Atualiza o status de sincronização
            google_event.sync_status = 'synced'
            google_event.sync_error = None
            google_event.save()
            
            return google_event
            
        except HttpError as e:
            # Salva erro de sincronização
            google_event.sync_status = 'error'
            google_event.sync_error = str(e)
            google_event.save()
            raise Exception(f"Erro ao atualizar evento no Google Calendar: {str(e)}")
    
    def delete_event(self, google_event: GoogleCalendarEvent):
        """
        Exclui um evento do Google Calendar.
        """
        try:
            # Exclui o evento do Google Calendar
            self.service.events().delete(
                calendarId=self.integration.calendar_id,
                eventId=google_event.google_event_id
            ).execute()
            
            # Remove o mapeamento do banco
            google_event.delete()
            
        except HttpError as e:
            raise Exception(f"Erro ao excluir evento do Google Calendar: {str(e)}")
    
    def sync_from_google(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, int]:
        """
        Sincroniza eventos do Google Calendar para o sistema.
        """
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now() + timedelta(days=365)
        
        # Cria log de sincronização
        sync_log = GoogleCalendarSyncLog.objects.create(
            integration=self.integration,
            sync_type='from_google',
            started_at=timezone.now()
        )
        
        try:
            # Busca eventos do Google Calendar
            events_result = self.service.events().list(
                calendarId=self.integration.calendar_id,
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Processa cada evento
            for event in events:
                self._process_google_event(event)
            
            # Atualiza log de sincronização
            sync_log.status = 'success'
            sync_log.completed_at = timezone.now()
            sync_log.save()
            
            return {
                'events_processed': len(events),
                'events_created': sync_log.events_created,
                'events_updated': sync_log.events_updated,
                'events_conflicted': sync_log.events_conflicted
            }
            
        except Exception as e:
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            sync_log.completed_at = timezone.now()
            sync_log.save()
            raise Exception(f"Erro na sincronização do Google Calendar: {str(e)}")
    
    def _prepare_event_data(self, agendamento: Agendamento) -> Dict[str, Any]:
        """
        Prepara os dados do evento para o Google Calendar.
        """
        # Formata as datas
        start_time = agendamento.inicio.isoformat()
        end_time = agendamento.fim.isoformat()
        
        # Prepara a descrição
        description_parts = []
        if agendamento.servico.descricao:
            description_parts.append(f"Serviço: {agendamento.servico.descricao}")
        if agendamento.observacoes:
            description_parts.append(f"Observações: {agendamento.observacoes}")
        if agendamento.preco_final:
            description_parts.append(f"Preço: R$ {agendamento.preco_final:.2f}")
        
        description = "\n".join(description_parts)
        
        # Prepara o evento
        event_data = {
            'summary': f"{agendamento.servico.nome} - {agendamento.cliente.username}",
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Sao_Paulo'
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Sao_Paulo'
            },
            'attendees': [
                {'email': agendamento.cliente.email, 'displayName': agendamento.cliente.username},
                {'email': agendamento.ator.email, 'displayName': agendamento.ator.username}
            ],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 dia antes
                    {'method': 'popup', 'minutes': 60}  # 1 hora antes
                ]
            },
            'extendedProperties': {
                'private': {
                    'agendamento_id': str(agendamento.id),
                    'servico_id': str(agendamento.servico.id)
                }
            }
        }
        
        return event_data
    
    def _process_google_event(self, event: Dict[str, Any]):
        """
        Processa um evento do Google Calendar.
        """
        try:
            # Verifica se é um evento do sistema (tem extendedProperties)
            extended_props = event.get('extendedProperties', {}).get('private', {})
            agendamento_id = extended_props.get('agendamento_id')
            
            if agendamento_id:
                # É um evento criado pelo sistema, não processa
                return
            
            # Verifica se já existe um agendamento para este evento
            google_event = GoogleCalendarEvent.objects.filter(
                google_event_id=event['id']
            ).first()
            
            if google_event:
                # Atualiza agendamento existente
                self._update_agendamento_from_google_event(google_event.agendamento, event)
            else:
                # Cria novo agendamento
                self._create_agendamento_from_google_event(event)
                
        except Exception as e:
            print(f"Erro ao processar evento do Google Calendar: {str(e)}")
    
    def _create_agendamento_from_google_event(self, event: Dict[str, Any]):
        """
        Cria um agendamento baseado em um evento do Google Calendar.
        """
        # Extrai informações do evento
        start_time = datetime.fromisoformat(
            event['start']['dateTime'].replace('Z', '+00:00')
        )
        end_time = datetime.fromisoformat(
            event['end']['dateTime'].replace('Z', '+00:00')
        )
        
        # Busca o ator (usuário da integração)
        ator = self.integration.usuario
        
        # Cria um serviço padrão se não existir
        from apps.agendamentos.models import Servico
        servico, created = Servico.objects.get_or_create(
            nome=event['summary'],
            ator=ator,
            defaults={
                'descricao': event.get('description', ''),
                'duracao_minutos': int((end_time - start_time).total_seconds() / 60),
                'preco': 0,
                'empresa': ator.empresa,
                'ativo': True
            }
        )
        
        # Cria o agendamento
        agendamento = Agendamento.objects.create(
            cliente=ator,  # Temporário, pode ser atualizado depois
            ator=ator,
            servico=servico,
            inicio=start_time,
            fim=end_time,
            status='confirmado',
            observacoes=f"Evento sincronizado do Google Calendar: {event.get('description', '')}"
        )
        
        # Cria o mapeamento
        GoogleCalendarEvent.objects.create(
            agendamento=agendamento,
            google_event_id=event['id'],
            google_calendar_id=self.integration.calendar_id,
            sync_status='synced'
        )
    
    def _update_agendamento_from_google_event(self, agendamento: Agendamento, event: Dict[str, Any]):
        """
        Atualiza um agendamento baseado em um evento do Google Calendar.
        """
        # Extrai informações do evento
        start_time = datetime.fromisoformat(
            event['start']['dateTime'].replace('Z', '+00:00')
        )
        end_time = datetime.fromisoformat(
            event['end']['dateTime'].replace('Z', '+00:00')
        )
        
        # Atualiza o agendamento
        agendamento.inicio = start_time
        agendamento.fim = end_time
        agendamento.observacoes = event.get('description', '')
        agendamento.save()


class GoogleCalendarOAuthService:
    """
    Serviço para gerenciar OAuth com Google Calendar.
    """
    
    @staticmethod
    def get_authorization_url(user: Usuario) -> str:
        """
        Gera URL de autorização OAuth para Google Calendar.
        """
        flow = Flow.from_client_config(
            {
                'web': {
                    'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                    'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [settings.GOOGLE_OAUTH_REDIRECT_URI]
                }
            },
            scopes=GoogleCalendarService.SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        # Salva o state para validação posterior
        # Em produção, use Redis ou banco de dados
        return authorization_url
    
    @staticmethod
    def handle_authorization_callback(user: Usuario, authorization_response: str) -> GoogleCalendarIntegration:
        """
        Processa o callback de autorização OAuth.
        """
        flow = Flow.from_client_config(
            {
                'web': {
                    'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                    'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                    'token_uri': 'https://oauth2.googleapis.com/token',
                    'redirect_uris': [settings.GOOGLE_OAUTH_REDIRECT_URI]
                }
            },
            scopes=GoogleCalendarService.SCOPES
        )
        flow.redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
        
        # Troca o código de autorização por tokens
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        # Cria ou atualiza a integração
        integration, created = GoogleCalendarIntegration.objects.update_or_create(
            usuario=user,
            defaults={
                'access_token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_expires_at': timezone.now() + timedelta(seconds=credentials.expiry),
                'sync_enabled': True
            }
        )
        
        return integration

