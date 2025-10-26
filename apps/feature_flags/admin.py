"""
Admin configuration for feature flags.
"""

from django.contrib import admin
from .models import FeatureFlag, LocalizationConfig


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    """Admin configuration for FeatureFlag model."""
    
    list_display = ['name', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(LocalizationConfig)
class LocalizationConfigAdmin(admin.ModelAdmin):
    """Admin configuration for LocalizationConfig model."""
    
    list_display = ['language_code', 'is_enabled', 'is_default', 'created_at']
    list_filter = ['is_enabled', 'is_default', 'language_code']
    search_fields = ['language_code']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['language_code']

