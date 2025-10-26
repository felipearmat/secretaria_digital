from celery import shared_task
from celery.schedules import crontab
from django.conf import settings
from .tasks import (
    sync_all_google_calendar_integrations,
    refresh_google_calendar_tokens,
    cleanup_google_calendar_sync_logs
)


# Periodic task configurations
CELERY_BEAT_SCHEDULE = {
    # Automatic synchronization with Google Calendar (every hour)
    'sync-google-calendar-hourly': {
        'task': 'apps.google_calendar.tasks.sync_all_google_calendar_integrations',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Token renewal (every hour)
    'refresh-google-calendar-tokens': {
        'task': 'apps.google_calendar.tasks.refresh_google_calendar_tokens',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour
    },
    
    # Old logs cleanup (daily at 2 AM)
    'cleanup-google-calendar-logs': {
        'task': 'apps.google_calendar.tasks.cleanup_google_calendar_sync_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}

# Add tasks to schedule if automatic synchronization is enabled
if getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
    # Incremental synchronization (every 15 minutes)
    CELERY_BEAT_SCHEDULE['sync-google-calendar-incremental'] = {
        'task': 'apps.google_calendar.tasks.sync_all_google_calendar_integrations',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    }

