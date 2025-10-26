from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from apps.appointments.serializers import AppointmentSerializer
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class GoogleCalendarIntegrationSerializer(serializers.ModelSerializer):
    """Serializer for GoogleCalendarIntegration."""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    is_token_expired = serializers.BooleanField(read_only=True)
    needs_refresh = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GoogleCalendarIntegration
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'calendar_id', 'sync_enabled', 'sync_direction',
            'notify_on_create', 'notify_on_update', 'notify_on_delete',
            'is_token_expired', 'needs_refresh', 'last_sync_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_token_expired', 'needs_refresh',
            'last_sync_at', 'created_at', 'updated_at'
        ]
    
    def validate_sync_direction(self, value):
        """Validates sync direction."""
        valid_directions = ['bidirectional', 'to_google', 'from_google']
        if value not in valid_directions:
            raise serializers.ValidationError(
                f"Direction must be one of: {', '.join(valid_directions)}"
            )
        return value


class GoogleCalendarIntegrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Google Calendar integration."""
    
    class Meta:
        model = GoogleCalendarIntegration
        fields = [
            'calendar_id', 'sync_enabled', 'sync_direction',
            'notify_on_create', 'notify_on_update', 'notify_on_delete'
        ]
    
    def create(self, validated_data):
        """Creates a new integration."""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class GoogleCalendarEventSerializer(serializers.ModelSerializer):
    """Serializer for GoogleCalendarEvent."""
    
    appointment_data = AppointmentSerializer(source='appointment', read_only=True)
    client_name = serializers.CharField(source='appointment.client.username', read_only=True)
    actor_name = serializers.CharField(source='appointment.actor.username', read_only=True)
    service_name = serializers.CharField(source='appointment.service.name', read_only=True)
    
    class Meta:
        model = GoogleCalendarEvent
        fields = [
            'id', 'appointment', 'appointment_data',
            'google_event_id', 'google_calendar_id',
            'sync_status', 'sync_error',
            'client_name', 'actor_name', 'service_name',
            'created_at', 'updated_at', 'last_sync_at'
        ]
        read_only_fields = [
            'id', 'appointment_data', 'client_name', 'actor_name', 'service_name',
            'created_at', 'updated_at', 'last_sync_at'
        ]


class GoogleCalendarSyncLogSerializer(serializers.ModelSerializer):
    """Serializer for GoogleCalendarSyncLog."""
    
    integration_user = serializers.CharField(
        source='integration.user.username', 
        read_only=True
    )
    duration_display = serializers.SerializerMethodField()
    events_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleCalendarSyncLog
        fields = [
            'id', 'integration', 'integration_user',
            'sync_type', 'status', 'error_message',
            'events_created', 'events_updated', 'events_deleted', 'events_conflicted',
            'events_summary', 'started_at', 'completed_at', 'duration_display'
        ]
        read_only_fields = [
            'id', 'integration_user', 'events_summary', 'duration_display',
            'started_at', 'completed_at'
        ]
    
    def get_duration_display(self, obj):
        """Returns formatted duration."""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            elif obj.duration_seconds < 3600:
                minutes = obj.duration_seconds // 60
                seconds = obj.duration_seconds % 60
                return f"{minutes}m {seconds}s"
            else:
                hours = obj.duration_seconds // 3600
                minutes = (obj.duration_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        return "-"
    
    def get_events_summary(self, obj):
        """Returns summary of processed events."""
        total = obj.events_created + obj.events_updated + obj.events_deleted
        return f"{total} events ({obj.events_created}C, {obj.events_updated}U, {obj.events_deleted}D)"


class GoogleCalendarOAuthSerializer(serializers.Serializer):
    """Serializer for Google Calendar OAuth."""
    
    authorization_url = serializers.URLField(read_only=True)
    state = serializers.CharField(max_length=255, required=False)
    
    def create(self, validated_data):
        """Creates OAuth authorization URL."""
        from .services import GoogleCalendarOAuthService
        
        user = self.context['request'].user
        authorization_url = GoogleCalendarOAuthService.get_authorization_url(user)
        
        return {
            'authorization_url': authorization_url
        }


class GoogleCalendarOAuthCallbackSerializer(serializers.Serializer):
    """Serializer for Google Calendar OAuth callback."""
    
    code = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255, required=False)
    
    def validate(self, attrs):
        """Validates callback data."""
        if not attrs.get('code'):
            raise serializers.ValidationError("Authorization code is required")
        return attrs
    
    def create(self, validated_data):
        """Processes OAuth callback."""
        from .services import GoogleCalendarOAuthService
        
        user = self.context['request'].user
        code = validated_data['code']
        
        # Simulates complete callback URL
        authorization_response = f"http://localhost:8000/google-calendar/callback/?code={code}"
        
        integration = GoogleCalendarOAuthService.handle_authorization_callback(
            user, authorization_response
        )
        
        return GoogleCalendarIntegrationSerializer(integration).data


class GoogleCalendarSyncSerializer(serializers.Serializer):
    """Serializer for Google Calendar synchronization."""
    
    sync_type = serializers.ChoiceField(
        choices=[
            ('full', 'Full Synchronization'),
            ('incremental', 'Incremental Synchronization'),
            ('manual', 'Manual Synchronization'),
        ],
        default='manual'
    )
    days_back = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=30,
        help_text="Number of days to search in the past"
    )
    days_forward = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=365,
        help_text="Number of days to search in the future"
    )
    
    def validate(self, attrs):
        """Validates synchronization data."""
        if attrs['days_back'] + attrs['days_forward'] > 400:
            raise serializers.ValidationError(
                "Sum of days cannot be greater than 400"
            )
        return attrs


class GoogleCalendarEventCreateSerializer(serializers.Serializer):
    """Serializer for creating Google Calendar event."""
    
    appointment_id = serializers.IntegerField()
    
    def validate_appointment_id(self, value):
        """Validates if appointment exists and belongs to user."""
        from apps.appointments.models import Appointment
        
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment not found")
        
        # Checks if user has permission
        user = self.context['request'].user
        if not (user == appointment.actor or user.is_admin or user.is_superadmin):
            raise serializers.ValidationError("You don't have permission for this appointment")
        
        return value
    
    def create(self, validated_data):
        """Creates Google Calendar event."""
        from .services import GoogleCalendarService
        from apps.appointments.models import Appointment
        
        appointment = Appointment.objects.get(id=validated_data['appointment_id'])
        user = self.context['request'].user
        
        # Finds user integration
        try:
            integration = GoogleCalendarIntegration.objects.get(
                user=user,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            raise serializers.ValidationError(
                "Google Calendar integration not found or disabled"
            )
        
        # Creates service and event
        service = GoogleCalendarService(integration)
        google_event = service.create_event(appointment)
        
        return GoogleCalendarEventSerializer(google_event).data

