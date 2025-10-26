from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from apps.appointments.models import Appointment
from .models import GoogleCalendarIntegration
from .tasks import (
    sync_appointment_to_google_calendar,
    remove_appointment_from_google_calendar
)


@receiver(post_save, sender=Appointment)
def sync_appointment_to_google(sender, instance, created, **kwargs):
    """
    Synchronizes appointment with Google Calendar when created or updated.
    """
    # Check if automatic synchronization is enabled
    if not getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
        return
    
    # Check if appointment should be synchronized
    if instance.status not in ['pending', 'confirmed']:
        return
    
    # Check if actor has active integration
    try:
        integration = GoogleCalendarIntegration.objects.get(
            user=instance.actor,
            sync_enabled=True,
            sync_direction__in=['bidirectional', 'to_google']
        )
    except GoogleCalendarIntegration.DoesNotExist:
        return
    
    # Schedule synchronization
    sync_appointment_to_google_calendar.delay(instance.id)


@receiver(post_delete, sender=Appointment)
def remove_appointment_from_google(sender, instance, **kwargs):
    """
    Removes appointment from Google Calendar when deleted.
    """
    # Checks if automatic synchronization is enabled
    if not getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
        return
    
    # Checks if actor has active integration
    try:
        integration = GoogleCalendarIntegration.objects.get(
            user=instance.actor,
            sync_enabled=True,
            sync_direction__in=['bidirectional', 'to_google']
        )
    except GoogleCalendarIntegration.DoesNotExist:
        return
    
    # Schedule removal
    remove_appointment_from_google_calendar.delay(instance.id)

