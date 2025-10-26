"""
Tests for Celery tasks in the appointments app.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta, date
from unittest.mock import patch
from apps.companies.models import Company
from apps.authentication.models import User
from .models import Service, Appointment, Recurrence, Block
from .tasks import (
    low_priority_generate_recurring_appointments,
    high_priority_validate_appointment_conflicts,
    low_priority_cleanup_old_appointments,
    _generate_daily_appointments,
    _generate_weekly_appointments,
    _generate_monthly_appointments,
    _check_block,
    _check_existing_appointment,
    _create_recurring_appointment
)


class AppointmentTasksTest(TestCase):
    """Tests for appointment tasks."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.client = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="user",
            company=self.company
        )
        
        self.service = Service.objects.create(
            name="Hair Cut",
            duration_minutes=30,
            base_price=25.00,
            company=self.company,
            actor=self.actor
        )
    
    def test_generate_daily_recurring_appointments(self):
        """Tests generation of daily recurring appointments."""
        # Create daily recurrence
        recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="daily",
            start_date=timezone.now().date()
        )
        
        # Execute the task
        result = low_priority_generate_recurring_appointments.delay()
        
        # Check if appointments were created
        appointments = Appointment.objects.filter(
            actor=self.actor,
            notes__contains="recurring"
        )
        
        self.assertGreater(appointments.count(), 0)
    
    def test_generate_weekly_recurring_appointments(self):
        """Tests generation of weekly recurring appointments."""
        # Create weekly recurrence
        recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="weekly",
            weekday=1,  # Tuesday
            start_date=timezone.now().date()
        )
        
        # Execute the task
        result = low_priority_generate_recurring_appointments.delay()
        
        # Check if appointments were created
        appointments = Appointment.objects.filter(
            actor=self.actor,
            notes__contains="recurring"
        )
        
        self.assertGreater(appointments.count(), 0)
    
    def test_generate_monthly_recurring_appointments(self):
        """Tests generation of monthly recurring appointments."""
        # Create monthly recurrence
        recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="monthly",
            day_of_month=15,
            start_date=timezone.now().date()
        )
        
        # Execute the task
        result = low_priority_generate_recurring_appointments.delay()
        
        # Check if appointments were created
        appointments = Appointment.objects.filter(
            actor=self.actor,
            notes__contains="recurring"
        )
        
        self.assertGreater(appointments.count(), 0)
    
    def test_validate_appointment_conflicts_no_conflict(self):
        """Tests appointment conflict validation with no conflict."""
        appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='pending'
        )
        
        # Execute the task
        result = high_priority_validate_appointment_conflicts.delay(appointment.id)
        
        # Check if appointment is still pending
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'pending')
    
    def test_validate_appointment_conflicts_with_conflict(self):
        """Tests appointment conflict validation with conflict."""
        # Create first appointment
        appointment1 = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='confirmed'
        )
        
        # Create second appointment with conflict
        appointment2 = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1, minutes=15),
            end_time=timezone.now() + timedelta(hours=1, minutes=45),
            status='pending'
        )
        
        # Execute the task
        result = high_priority_validate_appointment_conflicts.delay(appointment2.id)
        
        # Check if the second appointment was cancelled
        appointment2.refresh_from_db()
        self.assertEqual(appointment2.status, 'cancelled')
    
    def test_validate_appointment_conflicts_with_block(self):
        """Tests appointment conflict validation with block."""
        # Create block
        block = Block.objects.create(
            actor=self.actor,
            title="Vacation",
            block_type="vacation",
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Create appointment in blocked time
        appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1, minutes=30),
            end_time=timezone.now() + timedelta(hours=2, minutes=30),
            status='pending'
        )
        
        # Execute the task
        result = high_priority_validate_appointment_conflicts.delay(appointment.id)
        
        # Check if the appointment was cancelled
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')
    
    def test_cleanup_old_appointments(self):
        """Tests cleanup of old appointments."""
        # Create old appointment
        old_appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() - timedelta(days=100),
            end_time=timezone.now() - timedelta(days=100, minutes=30),
            status='cancelled'
        )
        
        # Create recent appointment
        recent_appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='pending'
        )
        
        # Execute the task
        result = low_priority_clean_old_appointments.delay()
        
        # Check if only the old appointment was removed
        self.assertFalse(Appointment.objects.filter(id=old_appointment.id).exists())
        self.assertTrue(Appointment.objects.filter(id=recent_appointment.id).exists())
    
    def test_check_block(self):
        """Tests block verification."""
        # Create block
        block = Block.objects.create(
            actor=self.actor,
            title="Vacation",
            block_type="vacation",
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2)
        )
        
        # Test blocked time
        date = timezone.now().date()
        start_time = datetime.strptime("01:30", "%H:%M").time()
        end_time = datetime.strptime("02:30", "%H:%M").time()
        
        self.assertTrue(_check_block(self.actor, date, start_time, end_time))
        
        # Test unblocked time
        start_time = datetime.strptime("03:00", "%H:%M").time()
        end_time = datetime.strptime("04:00", "%H:%M").time()
        
        self.assertFalse(_check_block(self.actor, date, start_time, end_time))
    
    def test_check_existing_appointment(self):
        """Tests existing appointment verification."""
        # Create appointment
        appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='confirmed'
        )
        
        # Test time with conflict
        date = appointment.start_time.date()
        start_time = appointment.start_time.time()
        end_time = appointment.end_time.time()
        
        self.assertTrue(_check_existing_appointment(self.actor, date, start_time, end_time))
        
        # Test time without conflict
        start_time = datetime.strptime("03:00", "%H:%M").time()
        end_time = datetime.strptime("04:00", "%H:%M").time()
        
        self.assertFalse(_check_existing_appointment(self.actor, date, start_time, end_time))
    
    def test_create_recurring_appointment(self):
        """Tests recurring appointment creation."""
        recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="daily",
            start_date=timezone.now().date()
        )
        
        date = timezone.now().date()
        appointment = _create_recurring_appointment(recurrence, date)
        
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.actor, self.actor)
        self.assertEqual(appointment.client, self.actor)
        self.assertEqual(appointment.status, 'confirmed')
        self.assertIn('recurring', appointment.notes)
