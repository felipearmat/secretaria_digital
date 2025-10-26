"""
Tests for the appointments app.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from apps.companies.models import Company
from apps.authentication.models import User
from .models import Service, Appointment, Recurrence, Block


class ServiceModelTest(TestCase):
    """Tests for the Service model."""
    
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
        
        self.service = Service.objects.create(
            name="Hair Cut",
            description="Men's haircut",
            duration_minutes=30,
            base_price=25.00,
            company=self.company,
            actor=self.actor
        )
    
    def test_service_creation(self):
        """Tests service creation."""
        self.assertEqual(self.service.name, "Hair Cut")
        self.assertEqual(self.service.duration_minutes, 30)
        self.assertEqual(self.service.base_price, 25.00)
        self.assertTrue(self.service.active)
    
    def test_service_str(self):
        """Tests service string representation."""
        expected = "Hair Cut - actor"
        self.assertEqual(str(self.service), expected)
    
    def test_service_clean_validation(self):
        """Tests service validation."""
        # Tests validation when actor doesn't belong to company
        other_company = Company.objects.create(
            name="Other Company",
            cnpj="98.765.432/0001-10"
        )
        
        invalid_service = Service(
            name="Invalid Service",
            duration_minutes=30,
            base_price=25.00,
            company=other_company,
            actor=self.actor  # Actor from different company
        )
        
        with self.assertRaises(ValidationError):
            invalid_service.clean()


class AppointmentModelTest(TestCase):
    """Tests for the Appointment model."""
    
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
        
        self.appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='pending'
        )
    
    def test_appointment_creation(self):
        """Tests appointment creation."""
        self.assertEqual(self.appointment.client, self.client)
        self.assertEqual(self.appointment.actor, self.actor)
        self.assertEqual(self.appointment.service, self.service)
        self.assertEqual(self.appointment.status, 'pending')
    
    def test_appointment_str(self):
        """Tests appointment string representation."""
        expected_start = self.appointment.start_time.strftime('%d/%m/%Y %H:%M')
        expected = f"Hair Cut - {expected_start}"
        self.assertEqual(str(self.appointment), expected)
    
    def test_appointment_clean_validation(self):
        """Tests appointment validation."""
        # Test validation when start >= end
        invalid_appointment = Appointment(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=2),
            end_time=timezone.now() + timedelta(hours=1),  # End before start
            status='pending'
        )
        
        with self.assertRaises(ValidationError):
            invalid_appointment.clean()
    
    def test_appointment_save_calculates_price(self):
        """Tests if price is automatically calculated on save."""
        appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=2),
            end_time=timezone.now() + timedelta(hours=2, minutes=30),
            status='pending'
        )
        
        # Price should be calculated automatically
        self.assertEqual(appointment.final_price, self.service.base_price)


class RecurrenceModelTest(TestCase):
    """Tests for the Recurrence model."""
    
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
    
    def test_recurrence_creation(self):
        """Tests recurrence creation."""
        recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="daily",
            start_date=timezone.now().date()
        )
        
        self.assertEqual(recurrence.actor, self.actor)
        self.assertEqual(recurrence.frequency, "daily")
        self.assertTrue(recurrence.is_active)
    
    def test_recurrence_clean_validation_weekly(self):
        """Tests weekly recurrence validation."""
        recurrence = Recurrence(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="weekly",
            start_date=timezone.now().date()
            # weekday not defined
        )
        
        with self.assertRaises(ValidationError):
            recurrence.clean()
    
    def test_recurrence_clean_validation_monthly(self):
        """Tests monthly recurrence validation."""
        recurrence = Recurrence(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="monthly",
            start_date=timezone.now().date()
            # day_of_month not defined
        )
        
        with self.assertRaises(ValidationError):
            recurrence.clean()


class BlockModelTest(TestCase):
    """Tests for the Block model."""
    
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
    
    def test_block_creation(self):
        """Tests block creation."""
        block = Block.objects.create(
            actor=self.actor,
            title="Vacation",
            description="Vacation period",
            block_type="vacation",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=7)
        )
        
        self.assertEqual(block.actor, self.actor)
        self.assertEqual(block.title, "Vacation")
        self.assertEqual(block.block_type, "vacation")
        self.assertTrue(block.is_active)
    
    def test_block_clean_validation(self):
        """Tests block validation."""
        # Tests validation when start >= end
        invalid_block = Block(
            actor=self.actor,
            title="Invalid Block",
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=1)  # End before start
        )
        
        with self.assertRaises(ValidationError):
            invalid_block.clean()
