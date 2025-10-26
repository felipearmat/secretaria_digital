from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from .services import GoogleCalendarService
from apps.appointments.models import Appointment


@shared_task
def sync_appointment_to_google_calendar(appointment_id: int):
    """
    Synchronizes a specific appointment to Google Calendar.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Find the actor's integration
        try:
            integration = GoogleCalendarIntegration.objects.get(
                user=appointment.actor,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            print(f"Google Calendar integration not found for {appointment.actor}")
            return
        
        # Check if synchronization is enabled for this type of operation
        if integration.sync_direction not in ['bidirectional', 'to_google']:
            print(f"Google Calendar synchronization not enabled for {appointment.actor}")
            return
        
        # Create the service
        service = GoogleCalendarService(integration)
        
        # Check if there's already a mapped event
        try:
            google_event = GoogleCalendarEvent.objects.get(appointment=appointment)
            
            # Update existing event
            service.update_event(google_event)
            print(f"Event updated in Google Calendar for appointment {appointment_id}")
            
        except GoogleCalendarEvent.DoesNotExist:
            # Create new event
            google_event = service.create_event(appointment)
            print(f"Event created in Google Calendar for appointment {appointment_id}")
        
        # Update last sync timestamp
        integration.last_sync_at = timezone.now()
        integration.save()
        
    except Appointment.DoesNotExist:
        print(f"Appointment {appointment_id} not found")
    except Exception as e:
        print(f"Error syncing appointment {appointment_id}: {str(e)}")


@shared_task
def remove_appointment_from_google_calendar(appointment_id: int):
    """
    Removes an appointment from Google Calendar.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Find the mapped event
        try:
            google_event = GoogleCalendarEvent.objects.get(appointment=appointment)
        except GoogleCalendarEvent.DoesNotExist:
            print(f"Google Calendar event not found for appointment {appointment_id}")
            return
        
        # Find the actor's integration
        try:
            integration = GoogleCalendarIntegration.objects.get(
                user=appointment.actor,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            print(f"Google Calendar integration not found for {appointment.actor}")
            return
        
        # Create the service
        service = GoogleCalendarService(integration)
        
        # Remove the event
        service.delete_event(google_event)
        print(f"Event removed from Google Calendar for appointment {appointment_id}")
        
    except Appointment.DoesNotExist:
        print(f"Appointment {appointment_id} not found")
    except Exception as e:
        print(f"Error removing appointment {appointment_id} from Google Calendar: {str(e)}")


@shared_task
def sync_from_google_calendar(integration_id: int, days_back: int = 30, days_forward: int = 365):
    """
    Synchronizes events from Google Calendar to the system.
    """
    try:
        integration = GoogleCalendarIntegration.objects.get(
            id=integration_id,
            sync_enabled=True
        )
        
        # Check if synchronization is enabled for this type of operation
        if integration.sync_direction not in ['bidirectional', 'from_google']:
            print(f"Google Calendar synchronization not enabled for {integration.user}")
            return
        
        # Calculate dates
        start_date = timezone.now() - timedelta(days=days_back)
        end_date = timezone.now() + timedelta(days=days_forward)
        
        # Create the service
        service = GoogleCalendarService(integration)
        
        # Synchronize events
        result = service.sync_from_google(start_date, end_date)
        
        print(f"Google Calendar synchronization completed for {integration.user}: {result}")
        
    except GoogleCalendarIntegration.DoesNotExist:
        print(f"Google Calendar integration {integration_id} not found")
    except Exception as e:
        print(f"Error in Google Calendar synchronization {integration_id}: {str(e)}")


@shared_task
def sync_all_google_calendar_integrations():
    """
    Synchronizes all active integrations with Google Calendar.
    """
    integrations = GoogleCalendarIntegration.objects.filter(
        sync_enabled=True,
        sync_direction__in=['bidirectional', 'from_google']
    )
    
    for integration in integrations:
        try:
            sync_from_google_calendar.delay(integration.id)
        except Exception as e:
            print(f"Error scheduling synchronization for {integration.user}: {str(e)}")


@shared_task
def sync_appointments_to_google_calendar():
    """
    Synchronizes all pending appointments to Google Calendar.
    """
    # Find appointments that haven't been synchronized
    appointments = Appointment.objects.filter(
        status__in=['pending', 'confirmed'],
        google_calendar_event__isnull=True
    ).select_related('actor')
    
    for appointment in appointments:
        try:
            # Check if the actor has active integration
            if GoogleCalendarIntegration.objects.filter(
                user=appointment.actor,
                sync_enabled=True,
                sync_direction__in=['bidirectional', 'to_google']
            ).exists():
                sync_appointment_to_google_calendar.delay(appointment.id)
        except Exception as e:
            print(f"Error scheduling synchronization for appointment {appointment.id}: {str(e)}")


@shared_task
def cleanup_google_calendar_sync_logs():
    """
    Remove old synchronization logs (older than 30 days).
    """
    cutoff_date = timezone.now() - timedelta(days=30)
    
    deleted_count = GoogleCalendarSyncLog.objects.filter(
        started_at__lt=cutoff_date
    ).delete()[0]
    
    print(f"Removed {deleted_count} old synchronization logs")


@shared_task
def refresh_google_calendar_tokens():
    """
    Renews expired access tokens.
    """
    integrations = GoogleCalendarIntegration.objects.filter(
        sync_enabled=True,
        token_expires_at__lt=timezone.now() + timedelta(minutes=5)
    )
    
    for integration in integrations:
        try:
            service = GoogleCalendarService(integration)
            # The service automatically renews the token if necessary
            print(f"Token renewed for {integration.user}")
        except Exception as e:
            print(f"Error renewing token for {integration.user}: {str(e)}")
            # Mark the integration as having an error
            integration.sync_enabled = False
            integration.save()

