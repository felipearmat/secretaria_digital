"""
Utility functions for feature flags and localization.
"""

from django.conf import settings
from django.utils import translation
from waffle import flag_is_active, switch_is_active
from .models import FeatureFlag, LocalizationConfig


def is_feature_enabled(flag_name, request=None):
    """
    Check if a feature flag is enabled.
    
    Args:
        flag_name (str): Name of the feature flag
        request: Django request object (optional)
    
    Returns:
        bool: True if feature is enabled, False otherwise
    """
    try:
        return flag_is_active(request, flag_name)
    except:
        # Fallback to database check
        try:
            flag = FeatureFlag.objects.get(name=flag_name)
            return flag.is_active
        except FeatureFlag.DoesNotExist:
            return False


def is_switch_enabled(switch_name, request=None):
    """
    Check if a switch is enabled.
    
    Args:
        switch_name (str): Name of the switch
        request: Django request object (optional)
    
    Returns:
        bool: True if switch is enabled, False otherwise
    """
    try:
        return switch_is_active(switch_name)
    except:
        return False


def get_available_languages():
    """
    Get list of available languages based on feature flags.
    
    Returns:
        list: List of available language codes
    """
    try:
        configs = LocalizationConfig.objects.filter(is_enabled=True)
        return [config.language_code for config in configs]
    except:
        # Fallback to settings
        return [lang[0] for lang in settings.LANGUAGES]


def get_default_language():
    """
    Get the default language code.
    
    Returns:
        str: Default language code
    """
    try:
        config = LocalizationConfig.objects.get(is_default=True)
        return config.language_code
    except LocalizationConfig.DoesNotExist:
        return settings.LANGUAGE_CODE


def is_language_enabled(language_code):
    """
    Check if a language is enabled.
    
    Args:
        language_code (str): Language code to check
    
    Returns:
        bool: True if language is enabled, False otherwise
    """
    try:
        config = LocalizationConfig.objects.get(language_code=language_code)
        return config.is_enabled
    except LocalizationConfig.DoesNotExist:
        return False


def get_user_language(request):
    """
    Get the appropriate language for a user.
    
    Args:
        request: Django request object
    
    Returns:
        str: Language code for the user
    """
    # Check if user has a preferred language
    if hasattr(request, 'user') and request.user.is_authenticated:
        if hasattr(request.user, 'preferred_language'):
            user_lang = request.user.preferred_language
            if is_language_enabled(user_lang):
                return user_lang
    
    # Check session language
    session_lang = request.session.get('language')
    if session_lang and is_language_enabled(session_lang):
        return session_lang
    
    # Check Accept-Language header
    accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
    if accept_lang:
        # Parse Accept-Language header
        for lang in accept_lang.split(','):
            lang_code = lang.split(';')[0].strip()
            if is_language_enabled(lang_code):
                return lang_code
    
    # Return default language
    return get_default_language()


def set_user_language(request, language_code):
    """
    Set the language for a user session.
    
    Args:
        request: Django request object
        language_code (str): Language code to set
    """
    if is_language_enabled(language_code):
        request.session['language'] = language_code
        translation.activate(language_code)
        request.LANGUAGE_CODE = language_code

