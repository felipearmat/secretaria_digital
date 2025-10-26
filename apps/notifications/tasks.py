"""
Celery tasks for the notifications app.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notification, NotificationConfig, NotificationTemplate
from apps.appointments.models import Appointment
from apps.authentication.models import User


@shared_task(queue='high')
def high_priority_send_appointment_notification(appointment_id, notification_type):
    """
    Sends high priority notification for appointments.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Create notification for client
        Notification.objects.create(
            user=appointment.client,
            title=f"Appointment {notification_type}",
            message=f"Your appointment for {appointment.service.name} was {notification_type}.",
            type=f'appointment_{notification_type}',
            priority='high',
            appointment=appointment
        )
        
        # Create notification for actor
        Notification.objects.create(
            user=appointment.actor,
            title=f"Appointment {notification_type}",   
            message=f"Appointment with {appointment.client.get_full_name()} was {notification_type}.",
            type=f'appointment_{notification_type}',
            priority='high',
            appointment=appointment
        )
        
        return f"Notifications sent for appointment {appointment_id}"
        
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"


@shared_task(queue='low')
def low_priority_send_appointment_reminder(appointment_id):
    """
    Sends appointment reminder (low priority).
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if appointment is still active
        if appointment.status not in ['pending', 'confirmed']:
            return f"Appointment {appointment_id} is not active"
        
        # Create reminder notification
        Notification.objects.create(
            user=appointment.client,
            title="Appointment Reminder",
            message=f"Reminder: You have an appointment tomorrow at {appointment.start_time.strftime('%H:%M')}.",
            type='reminder',
            priority='medium',
            appointment=appointment
        )
        
        return f"Reminder sent for appointment {appointment_id}"
        
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"


@shared_task(queue='low')
def low_priority_process_daily_reminders():
    """
    Processes daily reminders for next day appointments.
    """
    tomorrow = timezone.now().date() + timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        start_time__date=tomorrow,
        status__in=['pending', 'confirmed']
    )
    
    notifications_created = 0
    
    for appointment in appointments:
        # Check user configuration
        config, created = NotificationConfig.objects.get_or_create(   
            user=appointment.client
        )
        
        if config.whatsapp_reminders:
            low_priority_process_daily_reminders.delay(appointment.id)
            notifications_created += 1
    
    return f"Processed {notifications_created} reminders for {tomorrow}"


@shared_task(queue='high')
def high_priority_send_whatsapp(phone, message):
    """
    Sends message via WhatsApp (high priority).
    """
    # Here would be implemented the WhatsApp API integration
    # For now, just simulates the sending
    
    print(f"Sending WhatsApp to {phone}: {message}")
    
    # Simulates sending delay
    import time
    time.sleep(1)
    
    return f"WhatsApp sent to {phone}"


@shared_task(queue='low')
def low_priority_send_email(recipient, subject, body):
    """
    Sends email (low priority).
    """
    # Here would be implemented the email service integration
    # For now, just simulates the sending
    
    print(f"Sending email to {recipient}: {subject}")
    
    # Simulates sending delay
    import time
    time.sleep(2)
    
    return f"Email sent to {recipient}"


@shared_task(queue='low')
def low_priority_clean_old_notifications():
    """
    Removes old notifications (more than 30 days).
    """
    date_limit = timezone.now() - timedelta(days=30)
    
    notifications_removed = Notification.objects.filter(
        sent_at__lt=date_limit,
        read=True
    ).delete()[0]
    
    return f"Removed {notifications_removed} old notifications"
