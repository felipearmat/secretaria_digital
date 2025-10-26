"""
Celery tasks for the appointments app.
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Recurrence, Appointment, Block


@shared_task(queue='low')
def low_priority_generate_recurring_appointments():
    """
    Generates appointments based on active recurrences.
    """
    today = timezone.now().date()
    appointments_created = 0
    
    # Find active recurrences
    recurrences = Recurrence.objects.filter(
        is_active=True,
        start_date__lte=today
    )
    
    for recurrence in recurrences:
        # Check if recurrence is still valid
        if recurrence.end_date and recurrence.end_date < today:
            continue
        
        # Generate appointments based on frequency
        if recurrence.frequency == 'daily':
            appointments_created += _generate_daily_appointments(recurrence, today)
        elif recurrence.frequency == 'weekly':
            appointments_created += _generate_weekly_appointments(recurrence, today)
        elif recurrence.frequency == 'monthly':
            appointments_created += _generate_monthly_appointments(recurrence, today)
    
    return f"Generated {appointments_created} recurring appointments"


def _generate_daily_appointments(recurrence, start_date):
    """Generates daily appointments."""
    appointments_created = 0
    current_date = max(recurrence.start_date, start_date)
    end_date = recurrence.end_date or (current_date + timedelta(days=30))
    
    while current_date <= end_date:
        # Check if there's no block on this day
        if not _check_block(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
            # Check if appointment already exists at this time
            if not _check_existing_appointment(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
                _create_recurring_appointment(recurrence, current_date)
                appointments_created += 1
        
        current_date += timedelta(days=1)
    
    return appointments_created


def _generate_weekly_appointments(recurrence, start_date):
    """Generates weekly appointments."""
    appointments_created = 0
    current_date = max(recurrence.start_date, start_date)
    end_date = recurrence.end_date or (current_date + timedelta(days=30))
    
    # Find the next date with the correct weekday
    while current_date.weekday() != recurrence.weekday:
        current_date += timedelta(days=1)
    
    while current_date <= end_date:
        # Check if there's no block on this day
        if not _check_block(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
            # Check if appointment already exists at this time
            if not _check_existing_appointment(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
                _create_recurring_appointment(recurrence, current_date)
                appointments_created += 1
        
        current_date += timedelta(days=7)
    
    return appointments_created


def _generate_monthly_appointments(recurrence, start_date):
    """Generates monthly appointments."""
    appointments_created = 0
    current_date = max(recurrence.start_date, start_date)
    end_date = recurrence.end_date or (current_date + timedelta(days=90))
    
    # Find the next date with the correct day of month
    while current_date.day != recurrence.day_of_month:
        current_date += timedelta(days=1)
        if current_date.day == 1:  # Next month
            current_date = current_date.replace(day=recurrence.day_of_month)
    
    while current_date <= end_date:
        # Check if there's no block on this day
        if not _check_block(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
            # Check if appointment already exists at this time
            if not _check_existing_appointment(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
                _create_recurring_appointment(recurrence, current_date)
                appointments_created += 1
        
        # Next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1, day=recurrence.day_of_month)
        else:
            current_date = current_date.replace(month=current_date.month + 1, day=recurrence.day_of_month)
    
    return appointments_created


def _check_block(actor, date, start_time, end_time):
    """Checks if there's a block at the specified time."""
    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    
    blocks = Block.objects.filter(
        actor=actor,
        active=True,
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    )
    
    return blocks.exists()


def _check_existing_appointment(actor, date, start_time, end_time):
    """Checks if appointment already exists at the specified time."""
    start_datetime = datetime.combine(date, start_time)
    end_datetime = datetime.combine(date, end_time)
    
    appointments = Appointment.objects.filter(
        actor=actor,
        status__in=['pending', 'confirmed'],
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    )
    
    return appointments.exists()


def _create_recurring_appointment(recurrence, date):
    """Creates an appointment based on the recurrence."""
    start_datetime = datetime.combine(date, recurrence.start_time)
    end_datetime = datetime.combine(date, recurrence.end_time)
    
    # Creates a "blocked" appointment (not available for clients)
    appointment = Appointment.objects.create(
        actor=recurrence.actor,
        client=recurrence.actor,  # Self-scheduling
        service=None,  # Will be defined when necessary
        start_time=start_datetime,
        end_time=end_datetime,
        status='confirmed',
        notes=f'Recurring appointment - {recurrence.get_frequency_display()}'
    )
    
    return appointment


@shared_task(queue='high')
def high_priority_validate_appointment_conflicts(appointment_id):
    """
    Validates conflicts for a specific appointment.
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check conflicts with other appointments
        conflicts = Appointment.objects.filter(
            actor=appointment.actor,
            status__in=['pending', 'confirmed'],
            start_time__lt=appointment.end_time,
            end_time__gt=appointment.start_time
        ).exclude(id=appointment.id)
        
        if conflicts.exists():
            # Cancel the appointment if there's a conflict
            appointment.status = 'cancelled'
            appointment.notes = f"Cancelled due to conflict: {conflicts.first().id}"
            appointment.save()
            
            return f"Appointment {appointment_id} cancelled due to conflict"
        
        # Check conflicts with blocks
        blocks = Block.objects.filter(
            actor=appointment.actor,
            active=True,
            start_time__lt=appointment.end_time,
            end_time__gt=appointment.start_time
        )
        
        if blocks.exists():
            appointment.status = 'cancelled'
            appointment.notes = f"Cancelled due to block: {blocks.first().title}"
            appointment.save()
            
            return f"Appointment {appointment_id} cancelled due to block"
        
        return f"Appointment {appointment_id} validated successfully"
        
    except Appointment.DoesNotExist:
        return f"Appointment {appointment_id} not found"


@shared_task(queue='low')
def low_priority_clean_old_appointments():
    """
    Remove old and cancelled appointments.
    """
    date_limit = timezone.now().date() - timedelta(days=90)
    
    removed_appointments = Appointment.objects.filter(
        start_time__date__lt=date_limit,
        status__in=['cancelled', 'completed']
    ).delete()[0]
    
    return f"Removed {removed_appointments} old appointments"
