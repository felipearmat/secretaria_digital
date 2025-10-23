from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog


@admin.register(GoogleCalendarIntegration)
class GoogleCalendarIntegrationAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 'sync_enabled', 'sync_direction', 
        'last_sync_at', 'is_token_expired', 'created_at'
    ]
    list_filter = [
        'sync_enabled', 'sync_direction', 'created_at', 'last_sync_at'
    ]
    search_fields = ['usuario__username', 'usuario__email', 'calendar_id']
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']
    
    fieldsets = (
        ('Usuário', {
            'fields': ('usuario',)
        }),
        ('Credenciais OAuth', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Configurações de Sincronização', {
            'fields': (
                'calendar_id', 'sync_enabled', 'sync_direction'
            )
        }),
        ('Configurações de Notificação', {
            'fields': (
                'notify_on_create', 'notify_on_update', 'notify_on_delete'
            )
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'last_sync_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_token_expired(self, obj):
        if obj.is_token_expired:
            return format_html(
                '<span style="color: red;">Expirado</span>'
            )
        return format_html(
            '<span style="color: green;">Válido</span>'
        )
    is_token_expired.short_description = 'Token Status'
    is_token_expired.boolean = True


@admin.register(GoogleCalendarEvent)
class GoogleCalendarEventAdmin(admin.ModelAdmin):
    list_display = [
        'agendamento', 'google_event_id', 'sync_status', 
        'last_sync_at', 'created_at'
    ]
    list_filter = ['sync_status', 'created_at', 'last_sync_at']
    search_fields = [
        'agendamento__cliente__username', 
        'agendamento__ator__username',
        'google_event_id'
    ]
    readonly_fields = ['created_at', 'updated_at', 'last_sync_at']
    
    fieldsets = (
        ('Agendamento', {
            'fields': ('agendamento',)
        }),
        ('Google Calendar', {
            'fields': ('google_event_id', 'google_calendar_id')
        }),
        ('Sincronização', {
            'fields': ('sync_status', 'sync_error')
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at', 'last_sync_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'agendamento__cliente', 'agendamento__ator'
        )


@admin.register(GoogleCalendarSyncLog)
class GoogleCalendarSyncLogAdmin(admin.ModelAdmin):
    list_display = [
        'integration', 'sync_type', 'status', 'events_summary',
        'started_at', 'duration_display'
    ]
    list_filter = ['sync_type', 'status', 'started_at']
    search_fields = ['integration__usuario__username']
    readonly_fields = [
        'started_at', 'completed_at', 'duration_seconds',
        'events_created', 'events_updated', 'events_deleted', 'events_conflicted'
    ]
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Integração', {
            'fields': ('integration',)
        }),
        ('Detalhes da Sincronização', {
            'fields': ('sync_type', 'status', 'error_message')
        }),
        ('Resultados', {
            'fields': (
                'events_created', 'events_updated', 'events_deleted', 'events_conflicted'
            )
        }),
        ('Tempo', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        })
    )
    
    def events_summary(self, obj):
        total = obj.events_created + obj.events_updated + obj.events_deleted
        return f"{total} eventos ({obj.events_created}C, {obj.events_updated}U, {obj.events_deleted}D)"
    events_summary.short_description = 'Resumo dos Eventos'
    
    def duration_display(self, obj):
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            elif obj.duration_seconds < 3600:
                return f"{obj.duration_seconds // 60}m {obj.duration_seconds % 60}s"
            else:
                hours = obj.duration_seconds // 3600
                minutes = (obj.duration_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        return "-"
    duration_display.short_description = 'Duração'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'integration__usuario'
        )

