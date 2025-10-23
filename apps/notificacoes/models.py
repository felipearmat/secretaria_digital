"""
Modelos para o app de notificações.
"""

from django.db import models
from django.utils import timezone
from apps.autenticacao.models import Usuario
from apps.agendamentos.models import Agendamento


class Notificacao(models.Model):
    """Modelo para representar notificações do sistema."""
    
    TIPO_CHOICES = (
        ('agendamento_criado', 'Agendamento Criado'),
        ('agendamento_confirmado', 'Agendamento Confirmado'),
        ('agendamento_cancelado', 'Agendamento Cancelado'),
        ('agendamento_remarcado', 'Agendamento Remarcado'),
        ('lembrete', 'Lembrete'),
        ('pagamento_confirmado', 'Pagamento Confirmado'),
        ('cupom_disponivel', 'Cupom Disponível'),
        ('sistema', 'Notificação do Sistema'),
    )

    PRIORIDADE_CHOICES = (
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        verbose_name='Usuário'
    )
    titulo = models.CharField(
        max_length=255,
        verbose_name='Título'
    )
    mensagem = models.TextField(verbose_name='Mensagem')
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    prioridade = models.CharField(
        max_length=10,
        choices=PRIORIDADE_CHOICES,
        default='media',
        verbose_name='Prioridade'
    )
    lida = models.BooleanField(
        default=False,
        verbose_name='Lida'
    )
    agendamento = models.ForeignKey(
        Agendamento,
        on_delete=models.CASCADE,
        related_name="notificacoes",
        null=True,
        blank=True,
        verbose_name='Agendamento Relacionado'
    )
    data_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Envio'
    )
    data_leitura = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de Leitura'
    )

    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.titulo} - {self.usuario.username}"

    def marcar_como_lida(self):
        """Marca a notificação como lida."""
        if not self.lida:
            self.lida = True
            self.data_leitura = timezone.now()
            self.save()


class ConfiguracaoNotificacao(models.Model):
    """Modelo para configurações de notificação por usuário."""
    
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name="configuracao_notificacao",
        verbose_name='Usuário'
    )
    email_agendamentos = models.BooleanField(
        default=True,
        verbose_name='E-mail para Agendamentos'
    )
    email_pagamentos = models.BooleanField(
        default=True,
        verbose_name='E-mail para Pagamentos'
    )
    email_cupons = models.BooleanField(
        default=True,
        verbose_name='E-mail para Cupons'
    )
    whatsapp_agendamentos = models.BooleanField(
        default=True,
        verbose_name='WhatsApp para Agendamentos'
    )
    whatsapp_lembretes = models.BooleanField(
        default=True,
        verbose_name='WhatsApp para Lembretes'
    )
    notificacao_push = models.BooleanField(
        default=True,
        verbose_name='Notificação Push'
    )
    lembrete_antes_horas = models.PositiveIntegerField(
        default=24,
        verbose_name='Lembrete Antes (horas)'
    )

    class Meta:
        verbose_name = 'Configuração de Notificação'
        verbose_name_plural = 'Configurações de Notificação'

    def __str__(self):
        return f"Configuração - {self.usuario.username}"


class TemplateNotificacao(models.Model):
    """Modelo para templates de notificação."""
    
    TIPO_CHOICES = (
        ('email', 'E-mail'),
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
    )

    nome = models.CharField(
        max_length=100,
        verbose_name='Nome do Template'
    )
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        verbose_name='Tipo'
    )
    assunto = models.CharField(
        max_length=255,
        verbose_name='Assunto'
    )
    corpo = models.TextField(verbose_name='Corpo da Mensagem')
    variaveis = models.JSONField(
        default=list,
        verbose_name='Variáveis Disponíveis'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Template Ativo'
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )

    class Meta:
        verbose_name = 'Template de Notificação'
        verbose_name_plural = 'Templates de Notificação'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"
