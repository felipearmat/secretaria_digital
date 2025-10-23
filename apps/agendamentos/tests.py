"""
Testes para o app de agendamentos.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from apps.empresas.models import Empresa
from apps.autenticacao.models import Usuario
from .models import Servico, Agendamento, Recorrencia, Bloqueio


class ServicoModelTest(TestCase):
    """Testes para o modelo Servico."""
    
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
        
        self.servico = Servico.objects.create(
            nome="Corte de Cabelo",
            descricao="Corte masculino",
            duracao_minutos=30,
            preco_base=25.00,
            empresa=self.empresa,
            ator=self.ator
        )
    
    def test_servico_creation(self):
        """Testa a criação de um serviço."""
        self.assertEqual(self.servico.nome, "Corte de Cabelo")
        self.assertEqual(self.servico.duracao_minutos, 30)
        self.assertEqual(self.servico.preco_base, 25.00)
        self.assertTrue(self.servico.ativo)
    
    def test_servico_str(self):
        """Testa a representação string do serviço."""
        expected = "Corte de Cabelo - ator"
        self.assertEqual(str(self.servico), expected)
    
    def test_servico_clean_validation(self):
        """Testa validação do serviço."""
        # Testa validação quando ator não pertence à empresa
        outra_empresa = Empresa.objects.create(
            nome="Outra Empresa",
            cnpj="98.765.432/0001-10"
        )
        
        servico_invalido = Servico(
            nome="Serviço Inválido",
            duracao_minutos=30,
            preco_base=25.00,
            empresa=outra_empresa,
            ator=self.ator  # Ator de empresa diferente
        )
        
        with self.assertRaises(ValidationError):
            servico_invalido.clean()


class AgendamentoModelTest(TestCase):
    """Testes para o modelo Agendamento."""
    
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
    
    def test_agendamento_creation(self):
        """Testa a criação de um agendamento."""
        self.assertEqual(self.agendamento.cliente, self.cliente)
        self.assertEqual(self.agendamento.ator, self.ator)
        self.assertEqual(self.agendamento.servico, self.servico)
        self.assertEqual(self.agendamento.status, 'pendente')
    
    def test_agendamento_str(self):
        """Testa a representação string do agendamento."""
        expected_start = self.agendamento.inicio.strftime('%d/%m/%Y %H:%M')
        expected = f"Corte de Cabelo - {expected_start}"
        self.assertEqual(str(self.agendamento), expected)
    
    def test_agendamento_clean_validation(self):
        """Testa validação do agendamento."""
        # Testa validação quando início >= fim
        agendamento_invalido = Agendamento(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=2),
            fim=timezone.now() + timedelta(hours=1),  # Fim antes do início
            status='pendente'
        )
        
        with self.assertRaises(ValidationError):
            agendamento_invalido.clean()
    
    def test_agendamento_save_calcula_preco(self):
        """Testa se o preço é calculado automaticamente no save."""
        agendamento = Agendamento.objects.create(
            cliente=self.cliente,
            ator=self.ator,
            servico=self.servico,
            inicio=timezone.now() + timedelta(hours=2),
            fim=timezone.now() + timedelta(hours=2, minutes=30),
            status='pendente'
        )
        
        # O preço deve ser calculado automaticamente
        self.assertEqual(agendamento.preco_final, self.servico.preco_base)


class RecorrenciaModelTest(TestCase):
    """Testes para o modelo Recorrencia."""
    
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
    
    def test_recorrencia_creation(self):
        """Testa a criação de uma recorrência."""
        recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="diario",
            data_inicio=timezone.now().date()
        )
        
        self.assertEqual(recorrencia.ator, self.ator)
        self.assertEqual(recorrencia.frequencia, "diario")
        self.assertTrue(recorrencia.ativo)
    
    def test_recorrencia_clean_validation_semanal(self):
        """Testa validação de recorrência semanal."""
        recorrencia = Recorrencia(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="semanal",
            data_inicio=timezone.now().date()
            # dia_semana não definido
        )
        
        with self.assertRaises(ValidationError):
            recorrencia.clean()
    
    def test_recorrencia_clean_validation_mensal(self):
        """Testa validação de recorrência mensal."""
        recorrencia = Recorrencia(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="mensal",
            data_inicio=timezone.now().date()
            # dia_mes não definido
        )
        
        with self.assertRaises(ValidationError):
            recorrencia.clean()


class BloqueioModelTest(TestCase):
    """Testes para o modelo Bloqueio."""
    
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
    
    def test_bloqueio_creation(self):
        """Testa a criação de um bloqueio."""
        bloqueio = Bloqueio.objects.create(
            ator=self.ator,
            titulo="Férias",
            descricao="Período de férias",
            tipo="ferias",
            inicio=timezone.now() + timedelta(days=1),
            fim=timezone.now() + timedelta(days=7)
        )
        
        self.assertEqual(bloqueio.ator, self.ator)
        self.assertEqual(bloqueio.titulo, "Férias")
        self.assertEqual(bloqueio.tipo, "ferias")
        self.assertTrue(bloqueio.ativo)
    
    def test_bloqueio_clean_validation(self):
        """Testa validação do bloqueio."""
        # Testa validação quando início >= fim
        bloqueio_invalido = Bloqueio(
            ator=self.ator,
            titulo="Bloqueio Inválido",
            inicio=timezone.now() + timedelta(days=2),
            fim=timezone.now() + timedelta(days=1)  # Fim antes do início
        )
        
        with self.assertRaises(ValidationError):
            bloqueio_invalido.clean()
