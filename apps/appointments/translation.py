"""
Translation configuration for the appointments app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Service, Appointment, Recurrence, Block


class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'description')


class AppointmentTranslationOptions(TranslationOptions):
    fields = ('notes',)


class RecurrenceTranslationOptions(TranslationOptions):
    fields = ()


class BlockTranslationOptions(TranslationOptions):
    fields = ('title', 'description')


# Register translations
translator.register(Service, ServiceTranslationOptions)
translator.register(Appointment, AppointmentTranslationOptions)
translator.register(Recurrence, RecurrenceTranslationOptions)
translator.register(Block, BlockTranslationOptions)
