"""
Feature flags models for managing application features.
"""

from django.db import models
from django.utils import timezone


class FeatureFlag(models.Model):
    """Model for managing feature flags."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Flag Name')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    is_active = models.BooleanField(default=False, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        verbose_name = 'Feature Flag'
        verbose_name_plural = 'Feature Flags'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class LocalizationConfig(models.Model):
    """Model for managing localization configurations."""
    
    LANGUAGE_CHOICES = [
        ('pt-br', 'Portuguese (Brazil)'),
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
    ]
    
    language_code = models.CharField(
        max_length=10, 
        choices=LANGUAGE_CHOICES, 
        unique=True,
        verbose_name='Language Code'
    )
    is_enabled = models.BooleanField(default=True, verbose_name='Is Enabled')
    is_default = models.BooleanField(default=False, verbose_name='Is Default')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated at')
    
    class Meta:
        verbose_name = 'Localization Configuration'
        verbose_name_plural = 'Localization Configurations'
        ordering = ['language_code']
    
    def __str__(self):
        return f"{self.get_language_code_display()} ({'Enabled' if self.is_enabled else 'Disabled'})"
    
    def save(self, *args, **kwargs):
        """Ensure only one default language."""
        if self.is_default:
            LocalizationConfig.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
