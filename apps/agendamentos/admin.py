"""
Configuração do admin para o app de agendamentos.
"""

from django.contrib import admin
from .models import Servico, Agendamento, Recorrencia, Bloqueio


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ator', 'empresa', 'preco_base', 'duracao_minutos', 'ativo']
    list_filter = ['empresa', 'ator', 'ativo', 'criado_em']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['criado_em']


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ['servico', 'cliente', 'ator', 'inicio', 'fim', 'status', 'preco_final']
    list_filter = ['status', 'inicio', 'ator', 'servico__empresa']
    search_fields = ['cliente__username', 'ator__username', 'servico__nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    date_hierarchy = 'inicio'


@admin.register(Recorrencia)
class RecorrenciaAdmin(admin.ModelAdmin):
    list_display = ['ator', 'frequencia', 'inicio', 'fim', 'data_inicio', 'ativo']
    list_filter = ['frequencia', 'ativo', 'ator']
    search_fields = ['ator__username']


@admin.register(Bloqueio)
class BloqueioAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ator', 'tipo', 'inicio', 'fim', 'ativo']
    list_filter = ['tipo', 'ativo', 'inicio']
    search_fields = ['titulo', 'ator__username']
