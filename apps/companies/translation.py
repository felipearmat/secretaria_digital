"""
Translation configuration for the companies app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Company


class CompanyTranslationOptions(TranslationOptions):
    fields = ('name', 'address')


# Register translations
translator.register(Company, CompanyTranslationOptions)
