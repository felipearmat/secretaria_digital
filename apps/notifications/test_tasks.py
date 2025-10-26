"""
Tests for Celery tasks in the notifications app.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from apps.companies.models import Company
from apps.authentication.models import User
from apps.appointments.models import Service, Appointment
from .models import Notification, NotificationConfig
from .tasks import (
    high_priority_send_appointment_notification,
    low_priority_send_appointment_reminder,
    low_priority_process_daily_reminders,
    high_priority_send_whatsapp,
    low_priority_send_email,
    low_priority_cleanup_old_notifications
)


class NotificationTasksTest(TestCase):
    """Tests for notification tasks."""
    
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
    
    def test_send_appointment_notification_success(self):
        """Tests appointment notification sending with success."""
        result = high_priority_send_appointment_notification.delay(
            self.appointment.id, 'confirmed'
        )
        
        # Verifies if notifications were created
        client_notifications = Notification.objects.filter(
            user=self.client,
            type='appointment_confirmed'
        )
        actor_notifications = Notification.objects.filter(
            user=self.actor,
            type='appointment_confirmed'
        )
        
        self.assertEqual(client_notifications.count(), 1)
        self.assertEqual(actor_notifications.count(), 1)
    
    def test_send_appointment_notification_not_found(self):
        """Tests notification sending for non-existent appointment."""
        result = high_priority_send_appointment_notification.delay(999, 'confirmed')
        
        # Verifies no notifications were created
        notifications = Notification.objects.all()
        self.assertEqual(notifications.count(), 0)
    
    def test_send_appointment_reminder_success(self):
        """Tests appointment reminder sending with success."""
        result = low_priority_send_appointment_reminder.delay(self.appointment.id)
        
        # Verifies if reminder notification was created
        notifications = Notification.objects.filter(
            user=self.client,
            type='reminder'
        )
        
        self.assertEqual(notifications.count(), 1)
        self.assertIn('tomorrow', notifications.first().message)
    
    def test_send_appointment_reminder_inactive(self):
        """Tests reminder sending for inactive appointment."""
        # Cancels the appointment
        self.appointment.status = 'cancelled'
        self.appointment.save()
        
        result = low_priority_send_appointment_reminder.delay(self.appointment.id)
        
        # Verifies no notifications were created
        notifications = Notification.objects.filter(
            user=self.client,
            type='reminder'
        )
        
        self.assertEqual(notifications.count(), 0)
    
    def test_process_daily_reminders(self):
        """Tests daily reminders processing."""
        # Creates appointment for tomorrow
        tomorrow_appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, minutes=30),
            status='confirmed'
        )
        
        # Creates notification configuration
        NotificationConfig.objects.create(
            user=self.client,
            whatsapp_reminders=True
        )
        
        result = low_priority_process_daily_reminders.delay()
        
        # Verifies if reminder was sent
        notifications = Notification.objects.filter(
            user=self.client,
            type='reminder'
        )
        
        self.assertGreater(notifications.count(), 0)
    
    @patch('apps.notifications.tasks.print')
    def test_send_whatsapp(self, mock_print):
        """Tests WhatsApp sending."""
        phone = "11999999999"
        message = "Test message"
        
        result = high_priority_send_whatsapp.delay(phone, message)
        
        # Verifies if function was called
        mock_print.assert_called_with(f"Sending WhatsApp to {phone}: {message}")
    
    @patch('apps.notifications.tasks.print')
    def test_send_email(self, mock_print):
        """Tests email sending."""
        recipient = "test@example.com"
        subject = "Test"
        body = "Email body"
        
        result = low_priority_send_email.delay(recipient, subject, body)
        
        # Verifies if function was called
        mock_print.assert_called_with(f"Sending email to {recipient}: {subject}")
    
    def test_clean_old_notifications(self):
        """Tests old notifications cleanup."""
        # Creates old notification
        old_notification = Notification.objects.create(
            user=self.client,
            title="Old Notification",
            message="Old message",
            type="system",
            read=True,
            sent_at=timezone.now() - timedelta(days=35)
        )
        
        # Creates recent notification
        recent_notification = Notification.objects.create(
            user=self.client,
            title="Recent Notification",
            message="Recent message",
            type="system",
            read=False,
            sent_at=timezone.now() - timedelta(days=5)
        )
        
        result = low_priority_clean_old_notifications.delay()
        
        # Verifies only old notification was removed
        self.assertFalse(Notification.objects.filter(id=old_notification.id).exists())
        self.assertTrue(Notification.objects.filter(id=recent_notification.id).exists())
    
    def test_clean_old_unread_notifications(self):
        """Tests that unread notifications are not removed."""
        # Creates old unread notification
        old_unread_notification = Notification.objects.create(
            user=self.client,
            title="Old Unread Notification",
            message="Old unread message",
            type="system",
            read=False,
            sent_at=timezone.now() - timedelta(days=35)
        )
        
        result = low_priority_cleanup_old_notifications.delay()
        
        # Verifies that the notification was not removed
        self.assertTrue(Notification.objects.filter(id=old_unread_notification.id).exists())
