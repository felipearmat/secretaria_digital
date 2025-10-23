"""
Translation configuration for the companies app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Empresa


class EmpresaTranslationOptions(TranslationOptions):
    fields = ('nome', 'endereco')


# Register translations
translator.register(Empresa, EmpresaTranslationOptions)
