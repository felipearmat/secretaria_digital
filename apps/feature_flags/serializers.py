"""
Serializers for the feature flags app.
"""

from rest_framework import serializers
from .models import FeatureFlag, LocalizationConfig


class FeatureFlagSerializer(serializers.ModelSerializer):
    """Serializer for the FeatureFlag model."""
    
    class Meta:
        model = FeatureFlag
        fields = [
            'id', 'name', 'description', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LocalizationConfigSerializer(serializers.ModelSerializer):
    """Serializer for the LocalizationConfig model."""
    
    language_name = serializers.CharField(source='get_language_code_display', read_only=True)
    
    class Meta:
        model = LocalizationConfig
        fields = [
            'id', 'language_code', 'language_name', 'is_enabled', 
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

