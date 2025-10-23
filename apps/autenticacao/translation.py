"""
Translation configuration for the authentication app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Usuario


class UsuarioTranslationOptions(TranslationOptions):
    fields = ()


# Register translations
translator.register(Usuario, UsuarioTranslationOptions)
