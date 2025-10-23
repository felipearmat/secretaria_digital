"""
Views for the appointments app.
"""

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from .models import Service, Appointment, Recurrence, Block
from .serializers import (
    ServiceSerializer, AppointmentSerializer, AppointmentCreateSerializer,
    RecurrenceSerializer, BlockSerializer
)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing services."""
    
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters services based on the logged-in user."""
        user = self.request.user
        
        if user.is_superadmin:
            return Service.objects.all()
        elif user.is_admin:
            return Service.objects.filter(company=user.company)
        else:
            return Service.objects.filter(actor=user)
    
    @action(detail=False, methods=['get'])
    def by_actor(self, request):
        """Returns services for a specific actor."""
        actor_id = request.query_params.get('actor_id')
        if not actor_id:
            return Response(
                {'error': 'actor_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        services = Service.objects.filter(actor_id=actor_id, is_active=True)
        serializer = self.get_serializer(services, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing appointments."""
    
    queryset = Appointment.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'actor', 'client', 'service', 'start_time', 'end_time']
    search_fields = ['notes', 'service__name', 'actor__username', 'client__username']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['-start_time']
    
    def get_serializer_class(self):
        """Returns the appropriate serializer based on the action."""
        if self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    def get_queryset(self):
        """Filters appointments based on the logged-in user."""
        user = self.request.user
        queryset = Appointment.objects.all()
        
        if user.is_superadmin:
            return queryset
        elif user.is_admin:
            return queryset.filter(service__company=user.company)
        elif user.is_actor:
            return queryset.filter(actor=user)
        else:
            return queryset.filter(client=user)
        
        # Additional filters by URL parameters
        actor_id = self.request.query_params.get('actor_id')
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirms an appointment."""
        appointment = self.get_object()
        
        if not request.user.can_create_appointments(appointment.service.company):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'confirmed'
        appointment.save()
        
        # Send notification
        from apps.notificacoes.tasks import high_priority_send_appointment_notification
        high_priority_send_appointment_notification.delay(appointment.id, 'confirmed')
        
        return Response({'status': 'Appointment confirmed'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancels an appointment."""
        appointment = self.get_object()
        
        if not request.user.can_create_appointments(appointment.service.company):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        appointment.status = 'cancelled'
        appointment.save()
        
        # Send notification
        from apps.notificacoes.tasks import high_priority_send_appointment_notification
        high_priority_send_appointment_notification.delay(appointment.id, 'cancelled')
        
        return Response({'status': 'Appointment cancelled'})
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        """Returns available time slots for an actor on a specific date."""
        actor_id = request.query_params.get('actor_id')
        date = request.query_params.get('date')
        
        if not actor_id or not date:
            return Response(
                {'error': 'actor_id and date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Implement availability logic
        # For now, returns basic time slots
        available_times = []
        for hour in range(8, 18):  # 8am to 5pm
            available_times.append(f"{hour:02d}:00")
        
        return Response({'times': available_times})


class RecurrenceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing recurrences."""
    
    queryset = Recurrence.objects.all()
    serializer_class = RecurrenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters recurrences based on the logged-in user."""
        user = self.request.user
        
        if user.is_superadmin:
            return Recurrence.objects.all()
        elif user.is_admin:
            return Recurrence.objects.filter(actor__company=user.company)
        else:
            return Recurrence.objects.filter(actor=user)


class BlockViewSet(viewsets.ModelViewSet):
    """ViewSet for managing blocks."""
    
    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters blocks based on the logged-in user."""
        user = self.request.user
        
        if user.is_superadmin:
            return Block.objects.all()
        elif user.is_admin:
            return Block.objects.filter(actor__company=user.company)
        else:
            return Block.objects.filter(actor=user)
