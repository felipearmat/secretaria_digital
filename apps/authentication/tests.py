"""
Tests for the authentication app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.companies.models import Company
from .models import User

User = get_user_model()


class UserModelTest(TestCase):
    """Tests for User model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
    
    def test_user_creation(self):
        """Tests user creation."""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.role, "actor")
        self.assertEqual(self.user.company, self.company)
        self.assertTrue(self.user.is_active)
    
    def test_user_str(self):
        """Tests user string representation."""
        expected = "testuser (Actor/Service Provider)"
        self.assertEqual(str(self.user), expected)
    
    def test_user_is_superadmin(self):
        """Tests super admin verification."""
        self.assertFalse(self.user.is_superadmin)
        
        self.user.role = "superadmin"
        self.assertTrue(self.user.is_superadmin)
    
    def test_user_is_admin(self):
        """Tests admin verification."""
        self.assertFalse(self.user.is_admin)
        
        self.user.role = "admin"
        self.assertTrue(self.user.is_admin)
        
        self.user.role = "superadmin"
        self.assertTrue(self.user.is_admin)
    
    def test_user_is_manager(self):
        """Tests manager verification."""
        self.assertFalse(self.user.is_manager)
        
        self.user.role = "manager"
        self.assertTrue(self.user.is_manager)
        
        self.user.role = "admin"
        self.assertTrue(self.user.is_manager)
    
    def test_user_is_actor(self):
        """Tests actor verification."""
        self.assertTrue(self.user.is_actor)
        
        self.user.role = "user"
        self.assertFalse(self.user.is_actor)
    
    def test_can_manage_company(self):
        """Tests permission to manage company."""
        # Actor cannot manage company
        self.assertFalse(self.user.can_manage_company(self.company))
        
        # Admin can manage company
        self.user.role = "admin"
        self.assertTrue(self.user.can_manage_company(self.company))
        
        # Super admin can manage any company
        self.user.role = "superadmin"
        self.assertTrue(self.user.can_manage_company(self.company))
    
    def test_can_manage_actors(self):
        """Tests permission to manage actors."""
        # Actor cannot manage actors
        self.assertFalse(self.user.can_manage_actors(self.company))
        
        # Manager can manage actors
        self.user.role = "manager"
        self.assertTrue(self.user.can_manage_actors(self.company))
    
    def test_can_create_appointments(self):
        """Tests permission to create appointments."""
        # Actor can create appointments
        self.assertTrue(self.user.can_create_appointments(self.company))
        
        # User cannot create appointments
        self.user.role = "user"
        self.assertFalse(self.user.can_create_appointments(self.company))
