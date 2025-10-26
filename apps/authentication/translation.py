"""
Translation configuration for the authentication app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import User


class UserTranslationOptions(TranslationOptions):
    fields = ()


# Register translations
translator.register(User, UserTranslationOptions)
