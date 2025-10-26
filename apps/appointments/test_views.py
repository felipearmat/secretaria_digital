"""
Tests for the appointments app views.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.companies.models import Company
from apps.authentication.models import User
from .models import Service, Appointment, Recurrence, Block

User = get_user_model()


class AppointmentViewSetTest(APITestCase):
    """Tests for the AppointmentViewSet."""
    
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
        
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            role="admin",
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
    
    def test_list_appointments_actor(self):
        """Tests appointment listing for actor."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_appointments_client(self):
        """Tests appointment listing for client."""
        self.client.force_authenticate(user=self.client)
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_appointments_admin(self):
        """Tests appointment listing for admin."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('appointment-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_appointment(self):
        """Tests appointment creation."""
        self.client.force_authenticate(user=self.client)
        url = reverse('appointment-list')
        
        data = {
            'client': self.client.id,
            'actor': self.actor.id,
            'service': self.service.id,
            'start_time': (timezone.now() + timedelta(hours=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(hours=2, minutes=30)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 2)
    
    def test_confirm_appointment(self):
        """Tests appointment confirmation."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('appointment-confirm', kwargs={'pk': self.appointment.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'confirmed')
    
    def test_cancel_appointment(self):
        """Tests appointment cancellation."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('appointment-cancel', kwargs={'pk': self.appointment.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'cancelled')
    
    def test_actor_availability(self):
        """Tests actor availability query."""
        self.client.force_authenticate(user=self.client)
        url = reverse('appointment-availability')
        
        data = {
            'actor_id': self.actor.id,
            'date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('times', response.data)


class ServiceViewSetTest(APITestCase):
    """Tests for the ServiceViewSet."""
    
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
            duration_minutes=30,
            base_price=25.00,
            company=self.company,
            actor=self.actor
        )
    
    def test_list_services_actor(self):
        """Tests service listing for actor."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('service-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_services_by_actor(self):
        """Tests services by actor endpoint."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('service-by-actor')
        
        data = {'actor_id': self.actor.id}
        response = self.client.get(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_service(self):
        """Tests service creation."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('service-list')
        
        data = {
            'name': 'Beard',
            'duration_minutes': 20,
            'base_price': 15.00,
            'company': self.company.id,
            'actor': self.actor.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 2)


class RecurrenceViewSetTest(APITestCase):
    """Tests for the RecurrenceViewSet."""
    
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
        
        self.recurrence = Recurrence.objects.create(
            actor=self.actor,
            start_time=datetime.strptime("09:00", "%H:%M").time(),
            end_time=datetime.strptime("17:00", "%H:%M").time(),
            frequency="daily",
            start_date=timezone.now().date()
        )
    
    def test_list_recurrences_actor(self):
        """Tests recurrence listing for actor."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('recurrence-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_recurrence(self):
        """Tests recurrence creation."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('recurrence-list')
        
        data = {
            'actor': self.actor.id,
            'start_time': '10:00:00',
            'end_time': '18:00:00',
            'frequency': 'weekly',
            'weekday': 1,  # Tuesday
            'start_date': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recurrence.objects.count(), 2)


class BlockViewSetTest(APITestCase):
    """Tests for the BlockViewSet."""
    
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
        
        self.block = Block.objects.create(
            actor=self.actor,
            title="Vacation",
            block_type="vacation",
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=7)
        )
    
    def test_list_blocks_actor(self):
        """Tests block listing for actor."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('block-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_block(self):
        """Tests block creation."""
        self.client.force_authenticate(user=self.actor)
        url = reverse('block-list')
        
        data = {
            'actor': self.actor.id,
            'title': 'Maintenance',
            'block_type': 'maintenance',
            'start_time': (timezone.now() + timedelta(days=2)).isoformat(),
            'end_time': (timezone.now() + timedelta(days=2, hours=2)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Block.objects.count(), 2)
