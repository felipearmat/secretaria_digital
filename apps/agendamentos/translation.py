"""
Translation configuration for the appointments app.
"""

from modeltranslation.translator import translator, TranslationOptions
from .models import Servico, Agendamento, Recorrencia, Bloqueio


class ServicoTranslationOptions(TranslationOptions):
    fields = ('nome', 'descricao')


class AgendamentoTranslationOptions(TranslationOptions):
    fields = ('observacoes',)


class RecorrenciaTranslationOptions(TranslationOptions):
    fields = ()


class BloqueioTranslationOptions(TranslationOptions):
    fields = ('titulo', 'descricao')


# Register translations
translator.register(Servico, ServicoTranslationOptions)
translator.register(Agendamento, AgendamentoTranslationOptions)
translator.register(Recorrencia, RecorrenciaTranslationOptions)
translator.register(Bloqueio, BloqueioTranslationOptions)
