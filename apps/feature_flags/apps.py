"""
Feature flags app configuration.
"""

from django.apps import AppConfig


class FeatureFlagsConfig(AppConfig):
    """Feature flags app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feature_flags'
    verbose_name = 'Feature Flags'

