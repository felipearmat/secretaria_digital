"""
Views for the notifications app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Notification, NotificationConfig, NotificationTemplate
from .serializers import (
    NotificationSerializer, NotificationConfigSerializer,
    NotificationTemplateSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters notifications based on logged user."""
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Marks a notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Marks all user notifications as read."""
        notifications = self.get_queryset().filter(read=False)
        notifications.update(read=True, read_at=timezone.now())
        return Response({'status': 'All notifications have been marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Returns unread notifications."""
        notifications = self.get_queryset().filter(read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def counter(self, request):
        """Returns unread notifications counter."""
        count = self.get_queryset().filter(read=False).count()
        return Response({'count': count})


class NotificationConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification settings."""
    
    queryset = NotificationConfig.objects.all()
    serializer_class = NotificationConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters settings based on logged user."""
        return NotificationConfig.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Sets the user for the configuration."""
        serializer.save(user=self.request.user)


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notification templates."""
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filters templates based on logged user."""
        user = self.request.user
        
        if user.is_superadmin:
            return NotificationTemplate.objects.all()
        else:
            return NotificationTemplate.objects.filter(active=True)
