"""
Testes para o app de autenticação.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.empresas.models import Empresa
from .models import Usuario

User = get_user_model()


class UsuarioModelTest(TestCase):
    """Testes para o modelo Usuario."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.empresa = Empresa.objects.create(
            nome="Barbearia Teste",
            cnpj="12.345.678/0001-90"
        )
        
        self.usuario = Usuario.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="ator",
            empresa=self.empresa
        )
    
    def test_usuario_creation(self):
        """Testa a criação de um usuário."""
        self.assertEqual(self.usuario.username, "testuser")
        self.assertEqual(self.usuario.role, "ator")
        self.assertEqual(self.usuario.empresa, self.empresa)
        self.assertTrue(self.usuario.ativo)
    
    def test_usuario_str(self):
        """Testa a representação string do usuário."""
        expected = "testuser (Ator/Prestador de Serviço)"
        self.assertEqual(str(self.usuario), expected)
    
    def test_usuario_is_superadmin(self):
        """Testa verificação de super admin."""
        self.assertFalse(self.usuario.is_superadmin)
        
        self.usuario.role = "superadmin"
        self.assertTrue(self.usuario.is_superadmin)
    
    def test_usuario_is_admin(self):
        """Testa verificação de admin."""
        self.assertFalse(self.usuario.is_admin)
        
        self.usuario.role = "admin"
        self.assertTrue(self.usuario.is_admin)
        
        self.usuario.role = "superadmin"
        self.assertTrue(self.usuario.is_admin)
    
    def test_usuario_is_manager(self):
        """Testa verificação de gerente."""
        self.assertFalse(self.usuario.is_manager)
        
        self.usuario.role = "gerente"
        self.assertTrue(self.usuario.is_manager)
        
        self.usuario.role = "admin"
        self.assertTrue(self.usuario.is_manager)
    
    def test_usuario_is_actor(self):
        """Testa verificação de ator."""
        self.assertTrue(self.usuario.is_actor)
        
        self.usuario.role = "usuario"
        self.assertFalse(self.usuario.is_actor)
    
    def test_can_manage_company(self):
        """Testa permissão para gerenciar empresa."""
        # Ator não pode gerenciar empresa
        self.assertFalse(self.usuario.can_manage_company(self.empresa))
        
        # Admin pode gerenciar empresa
        self.usuario.role = "admin"
        self.assertTrue(self.usuario.can_manage_company(self.empresa))
        
        # Super admin pode gerenciar qualquer empresa
        self.usuario.role = "superadmin"
        self.assertTrue(self.usuario.can_manage_company(self.empresa))
    
    def test_can_manage_actors(self):
        """Testa permissão para gerenciar atores."""
        # Ator não pode gerenciar atores
        self.assertFalse(self.usuario.can_manage_actors(self.empresa))
        
        # Gerente pode gerenciar atores
        self.usuario.role = "gerente"
        self.assertTrue(self.usuario.can_manage_actors(self.empresa))
    
    def test_can_create_appointments(self):
        """Testa permissão para criar agendamentos."""
        # Ator pode criar agendamentos
        self.assertTrue(self.usuario.can_create_appointments(self.empresa))
        
        # Usuário não pode criar agendamentos
        self.usuario.role = "usuario"
        self.assertFalse(self.usuario.can_create_appointments(self.empresa))
