"""
Celery configuration for the secretariaVirtual project.
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Configure Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'secretariaVirtual.settings')

app = Celery('secretariaVirtual')

# Use a string so the worker can deserialize the configuration
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks from all registered apps
app.autodiscover_tasks()

# Task queue configuration
app.conf.task_queues = {
    'high': {
        'exchange': 'high',
        'routing_key': 'high',
    },
    'low': {
        'exchange': 'low',
        'routing_key': 'low',
    },
}

# Task routing
app.conf.task_routes = {
    'apps.*.tasks.high_priority_*': {'queue': 'high'},
    'apps.*.tasks.low_priority_*': {'queue': 'low'},
}

# Retry and timeout settings
app.conf.task_acks_late = True
app.conf.broker_connection_retry_on_startup = True
app.conf.task_annotations = {
    '*': {'max_retries': 2, 'default_retry_delay': 5}
}

# Minimum delay configuration for low queue (2 seconds)
app.conf.task_default_delay = 2

# Periodic tasks configuration
from celery.schedules import crontab

app.conf.beat_schedule = {
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
    
    # Cleanup old logs (daily at 2 AM)
    'cleanup-google-calendar-logs': {
        'task': 'apps.google_calendar.tasks.cleanup_google_calendar_sync_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    
    # Incremental synchronization (every 15 minutes) - only if enabled
    'sync-google-calendar-incremental': {
        'task': 'apps.google_calendar.tasks.sync_all_google_calendar_integrations',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
