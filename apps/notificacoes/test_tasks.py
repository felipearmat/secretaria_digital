"""
Testes para as tasks do Celery do app de notificações.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from apps.empresas.models import Empresa
from apps.autenticacao.models import Usuario
from apps.agendamentos.models import Servico, Agendamento
from .models import Notificacao, ConfiguracaoNotificacao
from .tasks import (
    high_priority_enviar_notificacao_agendamento,
    low_priority_enviar_lembrete_agendamento,
    low_priority_processar_lembretes_diarios,
    high_priority_enviar_whatsapp,
    low_priority_enviar_email,
    low_priority_limpar_notificacoes_antigas
)


class NotificacaoTasksTest(TestCase):
    """Testes para as tasks de notificações."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.empresa = Empresa.objects.create(
            nome="Barbearia Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.ator = Usuario.objects.create_user(
            username="ator",
            email="ator@example.com",
            password="testpass123",
            role="ator",
            empresa=self.empresa
        )
        
        self.cliente = Usuario.objects.create_user(
            username="cliente",
            email="cliente@example.com",
            password="testpass123",
            role="usuario",
            empresa=self.empresa
        )
        
        self.servico = Servico.objects.create(
            nome="Corte de Cabelo",
            duracao_minutos=30,
            preco_base=25.00,
            empresa=self.empresa,
            ator=self.ator
        )
        
        self.agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1, minutes=30),
            status='pendente'
        )
    
    def test_enviar_notificacao_agendamento_sucesso(self):
        """Testa envio de notificação de agendamento com sucesso."""
        result = high_priority_enviar_notificacao_agendamento.delay(
            self.agendamento.id, 'confirmado'
        )
        
        # Verifica se notificações foram criadas
        notificacoes_cliente = Notificacao.objects.filter(
            usuario=self.cliente,
            tipo='agendamento_confirmado'
        )
        notificacoes_ator = Notificacao.objects.filter(
            usuario=self.ator,
            tipo='agendamento_confirmado'
        )
        
        self.assertEqual(notificacoes_cliente.count(), 1)
        self.assertEqual(notificacoes_ator.count(), 1)
    
    def test_enviar_notificacao_agendamento_nao_encontrado(self):
        """Testa envio de notificação para agendamento inexistente."""
        result = high_priority_enviar_notificacao_agendamento.delay(999, 'confirmado')
        
        # Verifica se nenhuma notificação foi criada
        notificacoes = Notificacao.objects.all()
        self.assertEqual(notificacoes.count(), 0)
    
    def test_enviar_lembrete_agendamento_sucesso(self):
        """Testa envio de lembrete de agendamento com sucesso."""
        result = low_priority_enviar_lembrete_agendamento.delay(self.agendamento.id)
        
        # Verifica se notificação de lembrete foi criada
        notificacoes = Notificacao.objects.filter(
            usuario=self.cliente,
            tipo='lembrete'
        )
        
        self.assertEqual(notificacoes.count(), 1)
        self.assertIn('amanhã', notificacoes.first().mensagem)
    
    def test_enviar_lembrete_agendamento_inativo(self):
        """Testa envio de lembrete para agendamento inativo."""
        # Cancela o agendamento
        self.agendamento.status = 'cancelado'
        self.agendamento.save()
        
        result = low_priority_enviar_lembrete_agendamento.delay(self.agendamento.id)
        
        # Verifica se nenhuma notificação foi criada
        notificacoes = Notificacao.objects.filter(
            usuario=self.cliente,
            tipo='lembrete'
        )
        
        self.assertEqual(notificacoes.count(), 0)
    
    def test_processar_lembretes_diarios(self):
        """Testa processamento de lembretes diários."""
        # Cria agendamento para amanhã
        agendamento_amanha = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(days=1),
            fim=timezone.now() + timedelta(days=1, minutes=30),
            status='confirmado'
        )
        
        # Cria configuração de notificação
        ConfiguracaoNotificacao.objects.create(
            usuario=self.cliente,
            whatsapp_lembretes=True
        )
        
        result = low_priority_processar_lembretes_diarios.delay()
        
        # Verifica se lembrete foi enviado
        notificacoes = Notificacao.objects.filter(
            usuario=self.cliente,
            tipo='lembrete'
        )
        
        self.assertGreater(notificacoes.count(), 0)
    
    @patch('apps.notificacoes.tasks.print')
    def test_enviar_whatsapp(self, mock_print):
        """Testa envio de WhatsApp."""
        telefone = "11999999999"
        mensagem = "Teste de mensagem"
        
        result = high_priority_enviar_whatsapp.delay(telefone, mensagem)
        
        # Verifica se a função foi chamada
        mock_print.assert_called_with(f"Enviando WhatsApp para {telefone}: {mensagem}")
    
    @patch('apps.notificacoes.tasks.print')
    def test_enviar_email(self, mock_print):
        """Testa envio de e-mail."""
        destinatario = "teste@example.com"
        assunto = "Teste"
        corpo = "Corpo do e-mail"
        
        result = low_priority_enviar_email.delay(destinatario, assunto, corpo)
        
        # Verifica se a função foi chamada
        mock_print.assert_called_with(f"Enviando e-mail para {destinatario}: {assunto}")
    
    def test_limpar_notificacoes_antigas(self):
        """Testa limpeza de notificações antigas."""
        # Cria notificação antiga
        notificacao_antiga = Notificacao.objects.create(
            usuario=self.cliente,
            titulo="Notificação Antiga",
            mensagem="Mensagem antiga",
            tipo="sistema",
            lida=True,
            data_envio=timezone.now() - timedelta(days=35)
        )
        
        # Cria notificação recente
        notificacao_recente = Notificacao.objects.create(
            usuario=self.cliente,
            titulo="Notificação Recente",
            mensagem="Mensagem recente",
            tipo="sistema",
            lida=False,
            data_envio=timezone.now() - timedelta(days=5)
        )
        
        result = low_priority_limpar_notificacoes_antigas.delay()
        
        # Verifica se apenas a notificação antiga foi removida
        self.assertFalse(Notificacao.objects.filter(id=notificacao_antiga.id).exists())
        self.assertTrue(Notificacao.objects.filter(id=notificacao_recente.id).exists())
    
    def test_limpar_notificacoes_antigas_nao_lidas(self):
        """Testa que notificações não lidas não são removidas."""
        # Cria notificação antiga não lida
        notificacao_antiga_nao_lida = Notificacao.objects.create(
            usuario=self.cliente,
            titulo="Notificação Antiga Não Lida",
            mensagem="Mensagem antiga não lida",
            tipo="sistema",
            lida=False,
            data_envio=timezone.now() - timedelta(days=35)
        )
        
        result = low_priority_limpar_notificacoes_antigas.delay()
        
        # Verifica se a notificação não foi removida
        self.assertTrue(Notificacao.objects.filter(id=notificacao_antiga_nao_lida.id).exists())
