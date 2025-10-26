"""
Admin configuration for the notifications app.
"""

from django.contrib import admin
from .models import Notification, NotificationConfig, NotificationTemplate


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'priority', 'read', 'sent_at']
    list_filter = ['type', 'priority', 'read', 'sent_at']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['sent_at', 'read_at']


@admin.register(NotificationConfig)
class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_appointments', 'whatsapp_appointments', 'push_notification']
    search_fields = ['user__username']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'subject', 'active', 'created_at']
    list_filter = ['type', 'active', 'created_at']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at']
