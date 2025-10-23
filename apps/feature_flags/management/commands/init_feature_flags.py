"""
Management command to initialize feature flags and localization settings.
"""

from django.core.management.base import BaseCommand
from apps.feature_flags.models import FeatureFlag, LocalizationConfig


class Command(BaseCommand):
    """Command to initialize feature flags and localization."""
    
    help = 'Initialize feature flags and localization configurations'
    
    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write('Initializing feature flags and localization...')
        
        # Create feature flags
        feature_flags = [
            {
                'name': 'google_calendar_integration',
                'description': 'Enable Google Calendar integration',
                'is_active': True
            },
            {
                'name': 'whatsapp_notifications',
                'description': 'Enable WhatsApp notifications',
                'is_active': True
            },
            {
                'name': 'advanced_reporting',
                'description': 'Enable advanced reporting features',
                'is_active': False
            },
            {
                'name': 'multi_language_support',
                'description': 'Enable multi-language support',
                'is_active': True
            },
            {
                'name': 'recurring_appointments',
                'description': 'Enable recurring appointments feature',
                'is_active': True
            }
        ]
        
        for flag_data in feature_flags:
            flag, created = FeatureFlag.objects.get_or_create(
                name=flag_data['name'],
                defaults=flag_data
            )
            if created:
                self.stdout.write(f'Created feature flag: {flag.name}')
            else:
                self.stdout.write(f'Feature flag already exists: {flag.name}')
        
        # Create localization configurations
        localizations = [
            {
                'language_code': 'pt-br',
                'is_enabled': True,
                'is_default': True
            },
            {
                'language_code': 'en',
                'is_enabled': True,
                'is_default': False
            },
            {
                'language_code': 'es',
                'is_enabled': False,
                'is_default': False
            },
            {
                'language_code': 'fr',
                'is_enabled': False,
                'is_default': False
            }
        ]
        
        for loc_data in localizations:
            loc, created = LocalizationConfig.objects.get_or_create(
                language_code=loc_data['language_code'],
                defaults=loc_data
            )
            if created:
                self.stdout.write(f'Created localization config: {loc.language_code}')
            else:
                self.stdout.write(f'Localization config already exists: {loc.language_code}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized feature flags and localization!')
        )
