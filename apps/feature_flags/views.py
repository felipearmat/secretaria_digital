"""
Views for the feature flags app.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import translation
from .models import FeatureFlag, LocalizationConfig
from .serializers import FeatureFlagSerializer, LocalizationConfigSerializer
from .utils import get_user_language, set_user_language, is_language_enabled


class FeatureFlagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing feature flags."""
    
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter flags based on user permissions."""
        user = self.request.user
        
        if user.is_superadmin:
            return FeatureFlag.objects.all()
        else:
            # Regular users can only see active flags
            return FeatureFlag.objects.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active feature flags."""
        active_flags = FeatureFlag.objects.filter(is_active=True)
        serializer = self.get_serializer(active_flags, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """Toggle a feature flag."""
        if not request.user.is_superadmin:
            return Response(
                {'error': 'Only superusers can toggle feature flags'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        flag = self.get_object()
        flag.is_active = not flag.is_active
        flag.save()
        
        serializer = self.get_serializer(flag)
        return Response(serializer.data)


class LocalizationConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing localization configurations."""
    
    queryset = LocalizationConfig.objects.all()
    serializer_class = LocalizationConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter localization configs based on user permissions."""
        user = self.request.user
        
        if user.is_superadmin:
            return LocalizationConfig.objects.all()
        else:
            # Regular users can only see enabled languages
            return LocalizationConfig.objects.filter(is_enabled=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available languages."""
        available_languages = LocalizationConfig.objects.filter(is_enabled=True)
        serializer = self.get_serializer(available_languages, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user language."""
        current_lang = get_user_language(request)
        try:
            config = LocalizationConfig.objects.get(language_code=current_lang)
            serializer = self.get_serializer(config)
            return Response(serializer.data)
        except LocalizationConfig.DoesNotExist:
            return Response(
                {'error': 'Current language configuration not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def set_language(self, request, pk=None):
        """Set user language."""
        config = self.get_object()
        
        if not config.is_enabled:
            return Response(
                {'error': 'Language is not enabled'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        set_user_language(request, config.language_code)
        
        serializer = self.get_serializer(config)
        return Response(serializer.data)

