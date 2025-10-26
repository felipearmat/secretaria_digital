"""
Models for the notifications app.
"""

from django.db import models
from django.utils import timezone
from apps.authentication.models import User
from apps.appointments.models import Appointment


class Notification(models.Model):
    """Model to represent system notifications."""
    
    TYPE_CHOICES = (
        ('appointment_created', 'Appointment Created'),
        ('appointment_confirmed', 'Appointment Confirmed'),
        ('appointment_cancelled', 'Appointment Cancelled'),
        ('appointment_rescheduled', 'Appointment Rescheduled'),
        ('reminder', 'Reminder'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('coupon_available', 'Coupon Available'),
        ('system', 'System Notification'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name='User'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Title'
    )
    message = models.TextField(verbose_name='Message')
    type = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        verbose_name='Type'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='Priority'
    )
    read = models.BooleanField(
        default=False,
        verbose_name='Read'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True,
        verbose_name='Related Appointment'
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Sent at'
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Read at'
    )

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Marks the notification as read."""
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save()


class NotificationConfig(models.Model):
    """Model for user notification settings."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_config",
        verbose_name='User'
    )
    email_appointments = models.BooleanField(
        default=True,
        verbose_name='Email for Appointments'
    )
    email_payments = models.BooleanField(
        default=True,
        verbose_name='Email for Payments'
    )
    email_coupons = models.BooleanField(
        default=True,
        verbose_name='Email for Coupons'
    )
    whatsapp_appointments = models.BooleanField(
        default=True,
        verbose_name='WhatsApp for Appointments'
    )
    whatsapp_reminders = models.BooleanField(
        default=True,
        verbose_name='WhatsApp for Reminders'
    )
    push_notification = models.BooleanField(
        default=True,
        verbose_name='Push Notification'
    )
    reminder_before_hours = models.PositiveIntegerField(
        default=24,
        verbose_name='Reminder Before (hours)'
    )

    class Meta:
        verbose_name = 'Notification Configuration'
        verbose_name_plural = 'Notification Configurations'

    def __str__(self):
        return f"Configuration - {self.user.username}"


class NotificationTemplate(models.Model):
    """Model for notification templates."""
    
    TYPE_CHOICES = (
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    )

    name = models.CharField(
        max_length=100,
        verbose_name='Template Name'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Type'
    )
    subject = models.CharField(
        max_length=255,
        verbose_name='Subject'
    )
    body = models.TextField(verbose_name='Message Body')
    variables = models.JSONField(
        default=list,
        verbose_name='Available Variables'
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Active Template'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
