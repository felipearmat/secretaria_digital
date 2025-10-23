"""
Tests for the companies app.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Company


class CompanyModelTest(TestCase):
    """Tests for the Company model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90",
            phone="(11) 99999-9999",
            email="contact@barbershop.com",
            address="Test Street, 123"
        )
    
    def test_company_creation(self):
        """Tests company creation."""
        self.assertEqual(self.company.name, "Test Barber Shop")
        self.assertEqual(self.company.cnpj, "12.345.678/0001-90")
        self.assertTrue(self.company.is_active)
        self.assertIsNotNone(self.company.created_at)
    
    def test_company_str(self):
        """Tests company string representation."""
        self.assertEqual(str(self.company), "Test Barber Shop")
    
    def test_company_cnpj_unique(self):
        """Tests that CNPJ must be unique."""
        with self.assertRaises(Exception):
            Company.objects.create(
                name="Another Company",
                cnpj="12.345.678/0001-90"  # Same CNPJ
            )
    
    def test_company_total_users(self):
        """Tests total users calculation."""
        # Initially should be 0
        self.assertEqual(self.company.total_users, 0)
    
    def test_company_total_appointments_today(self):
        """Tests today's appointments calculation."""
        # Initially should be 0
        self.assertEqual(self.company.total_appointments_today, 0)
