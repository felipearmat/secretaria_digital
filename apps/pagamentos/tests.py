"""
Testes para o app de pagamentos.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from apps.empresas.models import Empresa
from apps.autenticacao.models import Usuario
from apps.agendamentos.models import Servico, Agendamento
from .models import Cupom, UsoCupom, Pagamento, CustoAtor, RelatorioFinanceiro


class CupomModelTest(TestCase):
    """Testes para o modelo Cupom."""
    
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
        
        self.cupom = Cupom.objects.create(
            codigo="DESCONTO10",
            empresa=self.empresa,
            ator=self.ator,
            tipo_desconto="percentual",
            valor_desconto=10.00,
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date() + timedelta(days=30),
            max_usos=100,
            max_usos_por_cliente=1
        )
    
    def test_cupom_creation(self):
        """Testa a criação de um cupom."""
        self.assertEqual(self.cupom.codigo, "DESCONTO10")
        self.assertEqual(self.cupom.empresa, self.empresa)
        self.assertEqual(self.cupom.tipo_desconto, "percentual")
        self.assertEqual(self.cupom.valor_desconto, 10.00)
        self.assertTrue(self.cupom.ativo)
    
    def test_cupom_str(self):
        """Testa a representação string do cupom."""
        expected = "DESCONTO10 - Barbearia Teste"
        self.assertEqual(str(self.cupom), expected)
    
    def test_cupom_is_valido(self):
        """Testa verificação de cupom válido."""
        # Cupom válido
        self.assertTrue(self.cupom.is_valido())
        
        # Cupom expirado
        self.cupom.data_fim = timezone.now().date() - timedelta(days=1)
        self.assertFalse(self.cupom.is_valido())
        
        # Cupom inativo
        self.cupom.ativo = False
        self.assertFalse(self.cupom.is_valido())
    
    def test_cupom_calcular_desconto_percentual(self):
        """Testa cálculo de desconto percentual."""
        valor_original = 100.00
        desconto = self.cupom.calcular_desconto(valor_original)
        self.assertEqual(desconto, 10.00)
    
    def test_cupom_calcular_desconto_valor_fixo(self):
        """Testa cálculo de desconto valor fixo."""
        self.cupom.tipo_desconto = "valor_fixo"
        self.cupom.valor_desconto = 15.00
        
        valor_original = 100.00
        desconto = self.cupom.calcular_desconto(valor_original)
        self.assertEqual(desconto, 15.00)
        
        # Testa quando desconto é maior que valor original
        valor_original = 10.00
        desconto = self.cupom.calcular_desconto(valor_original)
        self.assertEqual(desconto, 10.00)  # Não pode ser maior que o valor original


class UsoCupomModelTest(TestCase):
    """Testes para o modelo UsoCupom."""
    
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
        
        self.cupom = Cupom.objects.create(
            codigo="DESCONTO10",
            empresa=self.empresa,
            tipo_desconto="percentual",
            valor_desconto=10.00,
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date() + timedelta(days=30)
        )
        
        self.uso_cupom = UsoCupom.objects.create(
            cupom=self.cupom,
            cliente=self.cliente,
            agendamento=self.agendamento,
            valor_desconto_aplicado=2.50
        )
    
    def test_uso_cupom_creation(self):
        """Testa a criação de um uso de cupom."""
        self.assertEqual(self.uso_cupom.cupom, self.cupom)
        self.assertEqual(self.uso_cupom.cliente, self.cliente)
        self.assertEqual(self.uso_cupom.agendamento, self.agendamento)
        self.assertEqual(self.uso_cupom.valor_desconto_aplicado, 2.50)
    
    def test_uso_cupom_str(self):
        """Testa a representação string do uso de cupom."""
        expected = "DESCONTO10 - cliente"
        self.assertEqual(str(self.uso_cupom), expected)


class PagamentoModelTest(TestCase):
    """Testes para o modelo Pagamento."""
    
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
        
        self.pagamento = Pagamento.objects.create(
            agendamento=self.agendamento,
            valor=25.00,
            metodo="dinheiro",
            status="aprovado"
        )
    
    def test_pagamento_creation(self):
        """Testa a criação de um pagamento."""
        self.assertEqual(self.pagamento.agendamento, self.agendamento)
        self.assertEqual(self.pagamento.valor, 25.00)
        self.assertEqual(self.pagamento.metodo, "dinheiro")
        self.assertEqual(self.pagamento.status, "aprovado")
    
    def test_pagamento_str(self):
        """Testa a representação string do pagamento."""
        expected = f"Pagamento {self.pagamento.id} - {self.agendamento}"
        self.assertEqual(str(self.pagamento), expected)


class CustoAtorModelTest(TestCase):
    """Testes para o modelo CustoAtor."""
    
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
        
        self.custo = CustoAtor.objects.create(
            ator=self.ator,
            descricao="Compra de produtos",
            valor=50.00,
            data=timezone.now().date(),
            categoria="produtos"
        )
    
    def test_custo_ator_creation(self):
        """Testa a criação de um custo do ator."""
        self.assertEqual(self.custo.ator, self.ator)
        self.assertEqual(self.custo.descricao, "Compra de produtos")
        self.assertEqual(self.custo.valor, 50.00)
        self.assertEqual(self.custo.categoria, "produtos")
    
    def test_custo_ator_str(self):
        """Testa a representação string do custo."""
        expected = "ator - Compra de produtos - R$ 50.00"
        self.assertEqual(str(self.custo), expected)


class RelatorioFinanceiroModelTest(TestCase):
    """Testes para o modelo RelatorioFinanceiro."""
    
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
        
        self.relatorio = RelatorioFinanceiro.objects.create(
            empresa=self.empresa,
            ator=self.ator,
            tipo="completo",
            data_inicio=timezone.now().date(),
            data_fim=timezone.now().date() + timedelta(days=30),
            dados={"receitas": 1000, "custos": 300, "lucro": 700}
        )
    
    def test_relatorio_creation(self):
        """Testa a criação de um relatório financeiro."""
        self.assertEqual(self.relatorio.empresa, self.empresa)
        self.assertEqual(self.relatorio.ator, self.ator)
        self.assertEqual(self.relatorio.tipo, "completo")
        self.assertEqual(self.relatorio.dados["receitas"], 1000)
    
    def test_relatorio_str(self):
        """Testa a representação string do relatório."""
        expected = "Relatório Relatório Completo - Barbearia Teste"
        self.assertEqual(str(self.relatorio), expected)
