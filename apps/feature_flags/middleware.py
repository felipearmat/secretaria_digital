"""
Custom middleware for localization and feature flags.
"""

from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from .utils import get_user_language, is_language_enabled


class LocalizationMiddleware(MiddlewareMixin):
    """
    Middleware to handle user language preferences and feature flags.
    """
    
    def process_request(self, request):
        """Process the request to set the appropriate language."""
        # Get the appropriate language for the user
        language = get_user_language(request)
        
        # Check if the language is enabled
        if is_language_enabled(language):
            # Activate the language
            translation.activate(language)
            request.LANGUAGE_CODE = language
        else:
            # Fallback to default language
            from django.conf import settings
            translation.activate(settings.LANGUAGE_CODE)
            request.LANGUAGE_CODE = settings.LANGUAGE_CODE
        
        return None
    
    def process_response(self, request, response):
        """Process the response to ensure language is properly set."""
        # Ensure the language is still active in the response
        if hasattr(request, 'LANGUAGE_CODE'):
            response['Content-Language'] = request.LANGUAGE_CODE
        
        return response

