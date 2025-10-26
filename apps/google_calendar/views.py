from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from .serializers import (
    GoogleCalendarIntegrationSerializer,
    GoogleCalendarIntegrationCreateSerializer,
    GoogleCalendarEventSerializer,
    GoogleCalendarSyncLogSerializer,
    GoogleCalendarOAuthSerializer,
    GoogleCalendarOAuthCallbackSerializer,
    GoogleCalendarSyncSerializer,
    GoogleCalendarEventCreateSerializer
)
from .services import GoogleCalendarService, GoogleCalendarOAuthService
from .tasks import (
    sync_appointment_to_google_calendar,
    remove_appointment_from_google_calendar,
    sync_from_google_calendar,
    sync_all_google_calendar_integrations
)


class GoogleCalendarIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet to manage Google Calendar integrations."""
    
    queryset = GoogleCalendarIntegration.objects.all()
    serializer_class = GoogleCalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters integrations based on user."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarIntegration.objects.all()
        elif user.is_admin:
            return GoogleCalendarIntegration.objects.filter(
                user__company=user.company
            )
        else:
            return GoogleCalendarIntegration.objects.filter(user=user)
    
    def get_serializer_class(self):
        """Returns the appropriate serializer."""
        if self.action == 'create':
            return GoogleCalendarIntegrationCreateSerializer
        return GoogleCalendarIntegrationSerializer
    
    def perform_create(self, serializer):
        """Creates a new integration."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Initiates OAuth authorization process."""
        integration = self.get_object()
        
        serializer = GoogleCalendarOAuthSerializer(
            data={},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def callback(self, request, pk=None):
        """Processes OAuth callback."""
        integration = self.get_object()
        
        serializer = GoogleCalendarOAuthCallbackSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Synchronizes with Google Calendar."""
        integration = self.get_object()
        
        serializer = GoogleCalendarSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Schedule synchronization
        sync_from_google_calendar.delay(
            integration.id,
            serializer.validated_data['days_back'],
            serializer.validated_data['days_forward']
        )
        
        return Response({
            'message': 'Synchronization scheduled successfully',
            'integration_id': integration.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Tests connection with Google Calendar."""
        integration = self.get_object()
        
        try:
            service = GoogleCalendarService(integration)
            # Tries to list calendars to test the connection
            calendar_list = service.service.calendarList().list().execute()
            
            return Response({
                'status': 'success',
                'message': 'Google Calendar connection established successfully',
                'calendars_count': len(calendar_list.get('items', []))
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error connecting to Google Calendar: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Renews access token."""
        integration = self.get_object()
        
        try:
            service = GoogleCalendarService(integration)
            # The service automatically renews the token if necessary
            
            return Response({
                'status': 'success',
                'message': 'Token renewed successfully',
                'expires_at': integration.token_expires_at
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error renewing token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class GoogleCalendarEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet to view Google Calendar events."""
    
    queryset = GoogleCalendarEvent.objects.all()
    serializer_class = GoogleCalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters events based on user."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarEvent.objects.all()
        elif user.is_admin:
            return GoogleCalendarEvent.objects.filter(
                appointment__actor__company=user.company
            )
        else:
            return GoogleCalendarEvent.objects.filter(
                Q(appointment__actor=user) | Q(appointment__client=user)
            )
    
    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Creates event in Google Calendar."""
        serializer = GoogleCalendarEventCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def sync_to_google(self, request, pk=None):
        """Synchronizes specific event to Google Calendar."""
        event = self.get_object()
        
        # Schedule synchronization
        sync_appointment_to_google_calendar.delay(event.appointment.id)
        
        return Response({
            'message': 'Synchronization scheduled successfully',
            'event_id': event.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def remove_from_google(self, request, pk=None):
        """Removes event from Google Calendar."""
        event = self.get_object()
        
        # Schedule removal
        remove_appointment_from_google_calendar.delay(event.appointment.id)
        
        return Response({
            'message': 'Removal scheduled successfully',
            'event_id': event.id
        }, status=status.HTTP_202_ACCEPTED)


class GoogleCalendarSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet to view synchronization logs."""
    
    queryset = GoogleCalendarSyncLog.objects.all()
    serializer_class = GoogleCalendarSyncLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters logs based on user."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarSyncLog.objects.all()
        elif user.is_admin:
            return GoogleCalendarSyncLog.objects.filter(
                integration__user__company=user.company
            )
        else:
            return GoogleCalendarSyncLog.objects.filter(
                integration__user=user
            )
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Synchronizes all active integrations."""
        # Schedule global synchronization
        sync_all_google_calendar_integrations.delay()
        
        return Response({
            'message': 'Global synchronization scheduled successfully'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Returns synchronization statistics."""
        queryset = self.get_queryset()
        
        # General statistics
        total_syncs = queryset.count()
        successful_syncs = queryset.filter(status='success').count()
        error_syncs = queryset.filter(status='error').count()
        
        # Event statistics
        total_events_created = queryset.aggregate(
            total=models.Sum('events_created')
        )['total'] or 0
        
        total_events_updated = queryset.aggregate(
            total=models.Sum('events_updated')
        )['total'] or 0
        
        total_events_deleted = queryset.aggregate(
            total=models.Sum('events_deleted')
        )['total'] or 0
        
        # Last synchronization
        last_sync = queryset.order_by('-started_at').first()
        
        return Response({
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'error_syncs': error_syncs,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
            'total_events_created': total_events_created,
            'total_events_updated': total_events_updated,
            'total_events_deleted': total_events_deleted,
            'last_sync': GoogleCalendarSyncLogSerializer(last_sync).data if last_sync else None
        }, status=status.HTTP_200_OK)

