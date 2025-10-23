"""
Testes para as tasks do Celery do app de agendamentos.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta, date
from unittest.mock import patch
from apps.empresas.models import Empresa
from apps.autenticacao.models import Usuario
from .models import Servico, Agendamento, Recorrencia, Bloqueio
from .tasks import (
    low_priority_gerar_agendamentos_recorrentes,
    high_priority_validar_conflitos_agendamento,
    low_priority_limpar_agendamentos_antigos,
    _gerar_agendamentos_diarios,
    _gerar_agendamentos_semanais,
    _gerar_agendamentos_mensais,
    _verificar_bloqueio,
    _verificar_agendamento_existente,
    _criar_agendamento_recorrente
)


class AgendamentoTasksTest(TestCase):
    """Testes para as tasks de agendamentos."""
    
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
    
    def test_gerar_agendamentos_recorrentes_diarios(self):
        """Testa geração de agendamentos diários."""
        # Cria recorrência diária
        recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="diario",
            data_inicio=timezone.now().date()
        )
        
        # Executa a task
        result = low_priority_gerar_agendamentos_recorrentes.delay()
        
        # Verifica se agendamentos foram criados
        agendamentos = Agendamento.objects.filter(
            ator=self.ator,
            observacoes__contains="recorrente"
        )
        
        self.assertGreater(agendamentos.count(), 0)
    
    def test_gerar_agendamentos_recorrentes_semanais(self):
        """Testa geração de agendamentos semanais."""
        # Cria recorrência semanal
        recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="semanal",
            dia_semana=1,  # Terça-feira
            data_inicio=timezone.now().date()
        )
        
        # Executa a task
        result = low_priority_gerar_agendamentos_recorrentes.delay()
        
        # Verifica se agendamentos foram criados
        agendamentos = Agendamento.objects.filter(
            ator=self.ator,
            observacoes__contains="recorrente"
        )
        
        self.assertGreater(agendamentos.count(), 0)
    
    def test_gerar_agendamentos_recorrentes_mensais(self):
        """Testa geração de agendamentos mensais."""
        # Cria recorrência mensal
        recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="mensal",
            dia_mes=15,
            data_inicio=timezone.now().date()
        )
        
        # Executa a task
        result = low_priority_gerar_agendamentos_recorrentes.delay()
        
        # Verifica se agendamentos foram criados
        agendamentos = Agendamento.objects.filter(
            ator=self.ator,
            observacoes__contains="recorrente"
        )
        
        self.assertGreater(agendamentos.count(), 0)
    
    def test_validar_conflitos_agendamento_sem_conflito(self):
        """Testa validação de agendamento sem conflito."""
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1, minutes=30),
            status='pendente'
        )
        
        # Executa a task
        result = high_priority_validar_conflitos_agendamento.delay(agendamento.id)
        
        # Verifica se o agendamento ainda está pendente
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, 'pendente')
    
    def test_validar_conflitos_agendamento_com_conflito(self):
        """Testa validação de agendamento com conflito."""
        # Cria primeiro agendamento
        agendamento1 = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1, minutes=30),
            status='confirmado'
        )
        
        # Cria segundo agendamento com conflito
        agendamento2 = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1, minutes=15),
            fim=timezone.now() + timedelta(hours=1, minutes=45),
            status='pendente'
        )
        
        # Executa a task
        result = high_priority_validar_conflitos_agendamento.delay(agendamento2.id)
        
        # Verifica se o segundo agendamento foi cancelado
        agendamento2.refresh_from_db()
        self.assertEqual(agendamento2.status, 'cancelado')
    
    def test_validar_conflitos_agendamento_com_bloqueio(self):
        """Testa validação de agendamento com bloqueio."""
        # Cria bloqueio
        bloqueio = Bloqueio.objects.create(
            ator=self.ator,
            titulo="Férias",
            tipo="ferias",
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=2)
        )
        
        # Cria agendamento no horário bloqueado
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1, minutes=30),
            fim=timezone.now() + timedelta(hours=2, minutes=30),
            status='pendente'
        )
        
        # Executa a task
        result = high_priority_validar_conflitos_agendamento.delay(agendamento.id)
        
        # Verifica se o agendamento foi cancelado
        agendamento.refresh_from_db()
        self.assertEqual(agendamento.status, 'cancelado')
    
    def test_limpar_agendamentos_antigos(self):
        """Testa limpeza de agendamentos antigos."""
        # Cria agendamento antigo
        agendamento_antigo = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() - timedelta(days=100),
            fim=timezone.now() - timedelta(days=100, minutes=30),
            status='cancelado'
        )
        
        # Cria agendamento recente
        agendamento_recente = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1, minutes=30),
            status='pendente'
        )
        
        # Executa a task
        result = low_priority_limpar_agendamentos_antigos.delay()
        
        # Verifica se apenas o agendamento antigo foi removido
        self.assertFalse(Agendamento.objects.filter(id=agendamento_antigo.id).exists())
        self.assertTrue(Agendamento.objects.filter(id=agendamento_recente.id).exists())
    
    def test_verificar_bloqueio(self):
        """Testa verificação de bloqueio."""
        # Cria bloqueio
        bloqueio = Bloqueio.objects.create(
            ator=self.ator,
            titulo="Férias",
            tipo="ferias",
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=2)
        )
        
        # Testa horário bloqueado
        data = timezone.now().date()
        hora_inicio = datetime.strptime("01:30", "%H:%M").time()
        hora_fim = datetime.strptime("02:30", "%H:%M").time()
        
        self.assertTrue(_verificar_bloqueio(self.ator, data, hora_inicio, hora_fim))
        
        # Testa horário não bloqueado
        hora_inicio = datetime.strptime("03:00", "%H:%M").time()
        hora_fim = datetime.strptime("04:00", "%H:%M").time()
        
        self.assertFalse(_verificar_bloqueio(self.ator, data, hora_inicio, hora_fim))
    
    def test_verificar_agendamento_existente(self):
        """Testa verificação de agendamento existente."""
        # Cria agendamento
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1, minutes=30),
            status='confirmado'
        )
        
        # Testa horário com conflito
        data = agendamento.inicio.date()
        hora_inicio = agendamento.inicio.time()
        hora_fim = agendamento.fim.time()
        
        self.assertTrue(_verificar_agendamento_existente(self.ator, data, hora_inicio, hora_fim))
        
        # Testa horário sem conflito
        hora_inicio = datetime.strptime("03:00", "%H:%M").time()
        hora_fim = datetime.strptime("04:00", "%H:%M").time()
        
        self.assertFalse(_verificar_agendamento_existente(self.ator, data, hora_inicio, hora_fim))
    
    def test_criar_agendamento_recorrente(self):
        """Testa criação de agendamento recorrente."""
        recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="diario",
            data_inicio=timezone.now().date()
        )
        
        data = timezone.now().date()
        agendamento = _criar_agendamento_recorrente(recorrencia, data)
        
        self.assertIsNotNone(agendamento)
        self.assertEqual(agendamento.ator, self.ator)
        self.assertEqual(agendamento.cliente, self.ator)
        self.assertEqual(agendamento.status, 'confirmado')
        self.assertIn('recorrente', agendamento.observacoes)
