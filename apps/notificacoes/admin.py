"""
Configuração do admin para o app de notificações.
"""

from django.contrib import admin
from .models import Notificacao, ConfiguracaoNotificacao, TemplateNotificacao


@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'prioridade', 'lida', 'data_envio']
    list_filter = ['tipo', 'prioridade', 'lida', 'data_envio']
    search_fields = ['titulo', 'mensagem', 'usuario__username']
    readonly_fields = ['data_envio', 'data_leitura']


@admin.register(ConfiguracaoNotificacao)
class ConfiguracaoNotificacaoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'email_agendamentos', 'whatsapp_agendamentos', 'notificacao_push']
    search_fields = ['usuario__username']


@admin.register(TemplateNotificacao)
class TemplateNotificacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo', 'assunto', 'ativo', 'criado_em']
    list_filter = ['tipo', 'ativo', 'criado_em']
    search_fields = ['nome', 'assunto']
    readonly_fields = ['criado_em']
