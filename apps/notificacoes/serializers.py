"""
Serializers para o app de notificações.
"""

from rest_framework import serializers
from .models import Notificacao, ConfiguracaoNotificacao, TemplateNotificacao
from apps.autenticacao.serializers import UsuarioSerializer
from apps.agendamentos.serializers import AgendamentoSerializer


class NotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Notificacao."""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    agendamento_info = AgendamentoSerializer(source='agendamento', read_only=True)
    
    class Meta:
        model = Notificacao
        fields = [
            'id', 'usuario', 'titulo', 'mensagem', 'tipo', 'prioridade',
            'lida', 'agendamento', 'data_envio', 'data_leitura',
            'usuario_nome', 'agendamento_info'
        ]
        read_only_fields = ['id', 'data_envio', 'data_leitura']


class ConfiguracaoNotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo ConfiguracaoNotificacao."""
    
    usuario_nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    
    class Meta:
        model = ConfiguracaoNotificacao
        fields = [
            'id', 'usuario', 'email_agendamentos', 'email_pagamentos',
            'email_cupons', 'whatsapp_agendamentos', 'whatsapp_lembretes',
            'notificacao_push', 'lembrete_antes_horas', 'usuario_nome'
        ]


class TemplateNotificacaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo TemplateNotificacao."""
    
    class Meta:
        model = TemplateNotificacao
        fields = [
            'id', 'nome', 'tipo', 'assunto', 'corpo', 'variaveis',
            'ativo', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']
