from celery import shared_task
from celery.schedules import crontab
from django.conf import settings
from .tasks import (
    sync_all_google_calendar_integrations,
    refresh_google_calendar_tokens,
    cleanup_google_calendar_sync_logs
)


# Configurações de tarefas periódicas
CELERY_BEAT_SCHEDULE = {
    # Sincronização automática com Google Calendar (a cada hora)
    'sync-google-calendar-hourly': {
        'task': 'apps.google_calendar.tasks.sync_all_google_calendar_integrations',
        'schedule': crontab(minute=0),  # A cada hora
    },
    
    # Renovação de tokens (a cada 30 minutos)
    'refresh-google-calendar-tokens': {
        'task': 'apps.google_calendar.tasks.refresh_google_calendar_tokens',
        'schedule': crontab(minute=0, hour='*/1'),  # A cada hora
    },
    
    # Limpeza de logs antigos (diariamente às 2h)
    'cleanup-google-calendar-logs': {
        'task': 'apps.google_calendar.tasks.cleanup_google_calendar_sync_logs',
        'schedule': crontab(hour=2, minute=0),  # Diariamente às 2h
    },
}

# Adiciona as tarefas ao schedule se a sincronização automática estiver habilitada
if getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
    # Sincronização incremental (a cada 15 minutos)
    CELERY_BEAT_SCHEDULE['sync-google-calendar-incremental'] = {
        'task': 'apps.google_calendar.tasks.sync_all_google_calendar_integrations',
        'schedule': crontab(minute='*/15'),  # A cada 15 minutos
    }

