"""
Admin configuration for the appointments app.
"""

from django.contrib import admin
from .models import Service, Appointment, Recurrence, Block


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'actor', 'company', 'base_price', 'duration_minutes', 'is_active']
    list_filter = ['company', 'actor', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['service', 'client', 'actor', 'start_time', 'end_time', 'status', 'final_price']
    list_filter = ['status', 'start_time', 'actor', 'service__company']
    search_fields = ['client__username', 'actor__username', 'service__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'


@admin.register(Recurrence)
class RecurrenceAdmin(admin.ModelAdmin):
    list_display = ['actor', 'frequency', 'start_time', 'end_time', 'start_date', 'is_active']
    list_filter = ['frequency', 'is_active', 'actor']
    search_fields = ['actor__username']


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'actor', 'block_type', 'start_time', 'end_time', 'is_active']
    list_filter = ['block_type', 'is_active', 'start_time']
    search_fields = ['title', 'actor__username']
