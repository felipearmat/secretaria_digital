"""
Management command to test feature flags functionality.
"""

from django.core.management.base import BaseCommand
from apps.feature_flags.models import FeatureFlag, LocalizationConfig
from apps.feature_flags.utils import is_feature_enabled, get_available_languages, is_language_enabled


class Command(BaseCommand):
    """Command to test feature flags functionality."""
    
    help = 'Test feature flags and localization functionality'
    
    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Testing feature flags and localization...')
        
        # Test feature flags
        self.stdout.write('\n=== Testing Feature Flags ===')
        
        # Test Google Calendar integration flag
        if is_feature_enabled('google_calendar_integration'):
            self.stdout.write('✓ Google Calendar integration is enabled')
        else:
            self.stdout.write('✗ Google Calendar integration is disabled')
        
        # Test WhatsApp notifications flag
        if is_feature_enabled('whatsapp_notifications'):
            self.stdout.write('✓ WhatsApp notifications are enabled')
        else:
            self.stdout.write('✗ WhatsApp notifications are disabled')
        
        # Test advanced reporting flag
        if is_feature_enabled('advanced_reporting'):
            self.stdout.write('✓ Advanced reporting is enabled')
        else:
            self.stdout.write('✗ Advanced reporting is disabled')
        
        # Test localization
        self.stdout.write('\n=== Testing Localization ===')
        
        # Test available languages
        available_languages = get_available_languages()
        self.stdout.write(f'Available languages: {available_languages}')
        
        # Test specific language availability
        for lang in ['pt-br', 'en', 'es', 'fr']:
            if is_language_enabled(lang):
                self.stdout.write(f'✓ Language {lang} is enabled')
            else:
                self.stdout.write(f'✗ Language {lang} is disabled')
        
        # Test feature flag creation
        self.stdout.write('\n=== Testing Feature Flag Creation ===')
        
        test_flag, created = FeatureFlag.objects.get_or_create(
            name='test_flag',
            defaults={
                'description': 'Test flag for functionality testing',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write('✓ Test feature flag created successfully')
        else:
            self.stdout.write('✓ Test feature flag already exists')
        
        # Test localization config creation
        self.stdout.write('\n=== Testing Localization Config Creation ===')
        
        test_loc, created = LocalizationConfig.objects.get_or_create(
            language_code='test',
            defaults={
                'is_enabled': True,
                'is_default': False
            }
        )
        
        if created:
            self.stdout.write('✓ Test localization config created successfully')
        else:
            self.stdout.write('✓ Test localization config already exists')
        
        # Clean up test data
        test_flag.delete()
        test_loc.delete()
        self.stdout.write('✓ Test data cleaned up')
        
        self.stdout.write(
            self.style.SUCCESS('\nFeature flags and localization test completed successfully!')
        )
