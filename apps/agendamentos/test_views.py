"""
Testes para as views do app de agendamentos.
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.empresas.models import Empresa
from apps.autenticacao.models import Usuario
from .models import Servico, Agendamento, Recorrencia, Bloqueio

User = get_user_model()


class AgendamentoViewSetTest(APITestCase):
    """Testes para o AgendamentoViewSet."""
    
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
        
        self.admin = Usuario.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="testpass123",
            role="admin",
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
    
    def test_list_agendamentos_ator(self):
        """Testa listagem de agendamentos para ator."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('agendamento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_agendamentos_cliente(self):
        """Testa listagem de agendamentos para cliente."""
        self.client.force_authenticate(user=self.cliente)
        url = reverse('agendamento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_list_agendamentos_admin(self):
        """Testa listagem de agendamentos para admin."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('agendamento-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_agendamento(self):
        """Testa criação de agendamento."""
        self.client.force_authenticate(user=self.cliente)
        url = reverse('agendamento-list')
        
        data = {
            'cliente': self.cliente.id,
            'ator': self.ator.id,
            'servico': self.servico.id,
            'inicio': (timezone.now() + timedelta(hours=2)).isoformat(),
            'fim': (timezone.now() + timedelta(hours=2, minutes=30)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Agendamento.objects.count(), 2)
    
    def test_confirmar_agendamento(self):
        """Testa confirmação de agendamento."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('agendamento-confirmar', kwargs={'pk': self.agendamento.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.agendamento.refresh_from_db()
        self.assertEqual(self.agendamento.status, 'confirmado')
    
    def test_cancelar_agendamento(self):
        """Testa cancelamento de agendamento."""
        self.client.force_authenticate(user=self.admin)
        url = reverse('agendamento-cancelar', kwargs={'pk': self.agendamento.id})
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.agendamento.refresh_from_db()
        self.assertEqual(self.agendamento.status, 'cancelado')
    
    def test_disponibilidade_ator(self):
        """Testa consulta de disponibilidade do ator."""
        self.client.force_authenticate(user=self.cliente)
        url = reverse('agendamento-disponibilidade')
        
        data = {
            'ator_id': self.ator.id,
            'data': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        }
        
        response = self.client.get(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('horarios', response.data)


class ServicoViewSetTest(APITestCase):
    """Testes para o ServicoViewSet."""
    
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
            duracao_minutos=30,
            preco_base=25.00,
            empresa=self.empresa,
            ator=self.ator
        )
    
    def test_list_servicos_ator(self):
        """Testa listagem de serviços para ator."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('servico-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_servicos_por_ator(self):
        """Testa endpoint de serviços por ator."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('servico-por-ator')
        
        data = {'ator_id': self.ator.id}
        response = self.client.get(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_servico(self):
        """Testa criação de serviço."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('servico-list')
        
        data = {
            'nome': 'Barba',
            'duracao_minutos': 20,
            'preco_base': 15.00,
            'empresa': self.empresa.id,
            'ator': self.ator.id
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Servico.objects.count(), 2)


class RecorrenciaViewSetTest(APITestCase):
    """Testes para o RecorrenciaViewSet."""
    
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
        
        self.recorrencia = Recorrencia.objects.create(
            ator=self.ator,
            inicio=datetime.strptime("09:00", "%H:%M").time(),
            fim=datetime.strptime("17:00", "%H:%M").time(),
            frequencia="diario",
            data_inicio=timezone.now().date()
        )
    
    def test_list_recorrencias_ator(self):
        """Testa listagem de recorrências para ator."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('recorrencia-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_recorrencia(self):
        """Testa criação de recorrência."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('recorrencia-list')
        
        data = {
            'ator': self.ator.id,
            'inicio': '10:00:00',
            'fim': '18:00:00',
            'frequencia': 'semanal',
            'dia_semana': 1,  # Terça-feira
            'data_inicio': timezone.now().date().isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recorrencia.objects.count(), 2)


class BloqueioViewSetTest(APITestCase):
    """Testes para o BloqueioViewSet."""
    
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
        
        self.bloqueio = Bloqueio.objects.create(
            ator=self.ator,
            titulo="Férias",
            tipo="ferias",
            inicio=timezone.now() + timedelta(days=1),
            fim=timezone.now() + timedelta(days=7)
        )
    
    def test_list_bloqueios_ator(self):
        """Testa listagem de bloqueios para ator."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('bloqueio-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_bloqueio(self):
        """Testa criação de bloqueio."""
        self.client.force_authenticate(user=self.ator)
        url = reverse('bloqueio-list')
        
        data = {
            'ator': self.ator.id,
            'titulo': 'Manutenção',
            'tipo': 'manutencao',
            'inicio': (timezone.now() + timedelta(days=2)).isoformat(),
            'fim': (timezone.now() + timedelta(days=2, hours=2)).isoformat()
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Bloqueio.objects.count(), 2)
