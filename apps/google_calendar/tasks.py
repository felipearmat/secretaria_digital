from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from .services import GoogleCalendarService
from apps.agendamentos.models import Agendamento


@shared_task
def sync_agendamento_to_google_calendar(agendamento_id: int):
    """
    Sincroniza um agendamento específico para o Google Calendar.
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        # Busca a integração do ator
        try:
            integration = GoogleCalendarIntegration.objects.get(
                usuario=agendamento.ator,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            print(f"Integração Google Calendar não encontrada para {agendamento.ator}")
            return
        
        # Verifica se a sincronização está habilitada para este tipo de operação
        if integration.sync_direction not in ['bidirectional', 'to_google']:
            print(f"Sincronização para Google Calendar não habilitada para {agendamento.ator}")
            return
        
        # Cria o serviço
        service = GoogleCalendarService(integration)
        
        # Verifica se já existe um evento mapeado
        try:
            google_event = GoogleCalendarEvent.objects.get(agendamento=agendamento)
            
            # Atualiza o evento existente
            service.update_event(google_event)
            print(f"Evento atualizado no Google Calendar para agendamento {agendamento_id}")
            
        except GoogleCalendarEvent.DoesNotExist:
            # Cria novo evento
            google_event = service.create_event(agendamento)
            print(f"Evento criado no Google Calendar para agendamento {agendamento_id}")
        
        # Atualiza timestamp da última sincronização
        integration.last_sync_at = timezone.now()
        integration.save()
        
    except Agendamento.DoesNotExist:
        print(f"Agendamento {agendamento_id} não encontrado")
    except Exception as e:
        print(f"Erro ao sincronizar agendamento {agendamento_id}: {str(e)}")


@shared_task
def remove_agendamento_from_google_calendar(agendamento_id: int):
    """
    Remove um agendamento do Google Calendar.
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        # Busca o evento mapeado
        try:
            google_event = GoogleCalendarEvent.objects.get(agendamento=agendamento)
        except GoogleCalendarEvent.DoesNotExist:
            print(f"Evento Google Calendar não encontrado para agendamento {agendamento_id}")
            return
        
        # Busca a integração do ator
        try:
            integration = GoogleCalendarIntegration.objects.get(
                usuario=agendamento.ator,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            print(f"Integração Google Calendar não encontrada para {agendamento.ator}")
            return
        
        # Cria o serviço
        service = GoogleCalendarService(integration)
        
        # Remove o evento
        service.delete_event(google_event)
        print(f"Evento removido do Google Calendar para agendamento {agendamento_id}")
        
    except Agendamento.DoesNotExist:
        print(f"Agendamento {agendamento_id} não encontrado")
    except Exception as e:
        print(f"Erro ao remover agendamento {agendamento_id} do Google Calendar: {str(e)}")


@shared_task
def sync_from_google_calendar(integration_id: int, days_back: int = 30, days_forward: int = 365):
    """
    Sincroniza eventos do Google Calendar para o sistema.
    """
    try:
        integration = GoogleCalendarIntegration.objects.get(
            id=integration_id,
            sync_enabled=True
        )
        
        # Verifica se a sincronização está habilitada para este tipo de operação
        if integration.sync_direction not in ['bidirectional', 'from_google']:
            print(f"Sincronização do Google Calendar não habilitada para {integration.usuario}")
            return
        
        # Calcula as datas
        start_date = timezone.now() - timedelta(days=days_back)
        end_date = timezone.now() + timedelta(days=days_forward)
        
        # Cria o serviço
        service = GoogleCalendarService(integration)
        
        # Sincroniza eventos
        result = service.sync_from_google(start_date, end_date)
        
        print(f"Sincronização do Google Calendar concluída para {integration.usuario}: {result}")
        
    except GoogleCalendarIntegration.DoesNotExist:
        print(f"Integração Google Calendar {integration_id} não encontrada")
    except Exception as e:
        print(f"Erro na sincronização do Google Calendar {integration_id}: {str(e)}")


@shared_task
def sync_all_google_calendar_integrations():
    """
    Sincroniza todas as integrações ativas com Google Calendar.
    """
    integrations = GoogleCalendarIntegration.objects.filter(
        sync_enabled=True,
        sync_direction__in=['bidirectional', 'from_google']
    )
    
    for integration in integrations:
        try:
            sync_from_google_calendar.delay(integration.id)
        except Exception as e:
            print(f"Erro ao agendar sincronização para {integration.usuario}: {str(e)}")


@shared_task
def sync_agendamentos_to_google_calendar():
    """
    Sincroniza todos os agendamentos pendentes para o Google Calendar.
    """
    # Busca agendamentos que não foram sincronizados
    agendamentos = Agendamento.objects.filter(
        status__in=['pendente', 'confirmado'],
        google_calendar_event__isnull=True
    ).select_related('ator')
    
    for agendamento in agendamentos:
        try:
            # Verifica se o ator tem integração ativa
            if GoogleCalendarIntegration.objects.filter(
                usuario=agendamento.ator,
                sync_enabled=True,
                sync_direction__in=['bidirectional', 'to_google']
            ).exists():
                sync_agendamento_to_google_calendar.delay(agendamento.id)
        except Exception as e:
            print(f"Erro ao agendar sincronização para agendamento {agendamento.id}: {str(e)}")


@shared_task
def cleanup_google_calendar_sync_logs():
    """
    Remove logs de sincronização antigos (mais de 30 dias).
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = GoogleCalendarSyncLog.objects.filter(
        started_at__lt=cutoff_date
    ).delete()[0]
    
    print(f"Removidos {deleted_count} logs de sincronização antigos")


@shared_task
def refresh_google_calendar_tokens():
    """
    Renova tokens de acesso expirados.
    """
    integrations = GoogleCalendarIntegration.objects.filter(
        sync_enabled=True,
        token_expires_at__lt=timezone.now() + timedelta(minutes=5)
    )
    
    for integration in integrations:
        try:
            service = GoogleCalendarService(integration)
            # O serviço automaticamente renova o token se necessário
            print(f"Token renovado para {integration.usuario}")
        except Exception as e:
            print(f"Erro ao renovar token para {integration.usuario}: {str(e)}")
            # Marca a integração como com erro
            integration.sync_enabled = False
            integration.save()

