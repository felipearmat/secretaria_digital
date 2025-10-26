"""
Serializers for the notifications app.
"""

from rest_framework import serializers
from .models import Notification, NotificationConfig, NotificationTemplate
from apps.authentication.serializers import UserSerializer
from apps.appointments.serializers import AppointmentSerializer


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for the Notification model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    appointment_info = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type', 'priority',
            'read', 'appointment', 'sent_at', 'read_at',
            'user_name', 'appointment_info'
        ]
        read_only_fields = ['id', 'sent_at', 'read_at']


class NotificationConfigSerializer(serializers.ModelSerializer):
    """Serializer for the NotificationConfig model."""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = NotificationConfig
        fields = [
            'id', 'user', 'email_appointments', 'email_payments',
            'email_coupons', 'whatsapp_appointments', 'whatsapp_reminders',
            'push_notification', 'reminder_before_hours', 'user_name'
        ]


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for the NotificationTemplate model."""
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'type', 'subject', 'body', 'variables',
            'active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
