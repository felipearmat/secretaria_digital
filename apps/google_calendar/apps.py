from django.apps import AppConfig


class GoogleCalendarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.google_calendar'
    verbose_name = 'Google Calendar'
    
    def ready(self):
        import apps.google_calendar.signals

