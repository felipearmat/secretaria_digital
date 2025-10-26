"""
Tests for the payments app.
"""

from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from apps.companies.models import Company
from apps.authentication.models import User
from apps.appointments.models import Service, Appointment
from .models import Coupon, CouponUsage, Payment, ActorCost, FinancialReport


class CouponModelTest(TestCase):
    """Tests for Coupon model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.coupon = Coupon.objects.create(
            code="DISCOUNT10",
            company=self.company,
            actor=self.actor,
            discount_type="percentage",
            discount_value=10.00,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            max_uses=100,
            max_uses_per_client=1
        )
    
    def test_coupon_creation(self):
        """Tests coupon creation."""
        self.assertEqual(self.coupon.code, "DISCOUNT10")
        self.assertEqual(self.coupon.company, self.company)
        self.assertEqual(self.coupon.discount_type, "percentage")
        self.assertEqual(self.coupon.discount_value, 10.00)
        self.assertTrue(self.coupon.active)
    
    def test_coupon_str(self):
        """Tests coupon string representation."""
        expected = "DISCOUNT10 - Test Barber Shop"
        self.assertEqual(str(self.coupon), expected)
    
    def test_coupon_is_valid(self):
        """Tests valid coupon verification."""
        # Valid coupon
        self.assertTrue(self.coupon.is_valid())
        
        # Expired coupon
        self.coupon.end_date = timezone.now().date() - timedelta(days=1)
        self.assertFalse(self.coupon.is_valid())
        
        # Inactive coupon
        self.coupon.active = False
        self.assertFalse(self.coupon.is_valid())
    
    def test_coupon_calculate_discount_percentage(self):
        """Tests percentage discount calculation."""
        original_value = 100.00
        discount = self.coupon.calculate_discount(original_value)
        self.assertEqual(discount, 10.00)
    
    def test_coupon_calculate_discount_fixed_value(self):
        """Tests fixed value discount calculation."""
        self.coupon.discount_type = "fixed_value"
        self.coupon.discount_value = 15.00
        
        original_value = 100.00
        discount = self.coupon.calculate_discount(original_value)
        self.assertEqual(discount, 15.00)
        
        # Tests when discount is greater than original value
        original_value = 10.00
        discount = self.coupon.calculate_discount(original_value)
        self.assertEqual(discount, 10.00)  # Cannot be greater than original value


class CouponUsageModelTest(TestCase):
    """Tests for the CouponUsage model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.client = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="user",
            company=self.company
        )
        
        self.service = Service.objects.create(
            name="Haircut",
            duration_minutes=30,
            base_price=25.00,
            company=self.company,
            actor=self.actor
        )
        
        self.appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='pending'
        )
        
        self.coupon = Coupon.objects.create(
            code="DISCOUNT10",
            company=self.company,
            discount_type="percentage",
            discount_value=10.00,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30)
        )
        
        self.coupon_usage = CouponUsage.objects.create(
            coupon=self.coupon,
            client=self.client,
            appointment=self.appointment,
            discount_value_applied=2.50
        )
    
    def test_coupon_usage_creation(self):
        """Tests coupon usage creation."""
        self.assertEqual(self.coupon_usage.coupon, self.coupon)
        self.assertEqual(self.coupon_usage.client, self.client)
        self.assertEqual(self.coupon_usage.appointment, self.appointment)
        self.assertEqual(self.coupon_usage.discount_value_applied, 2.50)
    
    def test_coupon_usage_str(self):
        """Tests coupon usage string representation."""
        expected = "DISCOUNT10 - client"
        self.assertEqual(str(self.coupon_usage), expected)


class PaymentModelTest(TestCase):
    """Tests for Payment model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.client = User.objects.create_user(
            username="client",
            email="client@example.com",
            password="testpass123",
            role="user",
            company=self.company
        )
        
        self.service = Service.objects.create(
            name="Haircut",
            duration_minutes=30,
            base_price=25.00,
            company=self.company,
            actor=self.actor
        )
        
        self.appointment = Appointment.objects.create(
            client=self.client,
            actor=self.actor,
            service=self.service,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1, minutes=30),
            status='pending'
        )
        
        self.payment = Payment.objects.create(
            appointment=self.appointment,
            value=25.00,
            method="cash",
            status="approved"
        )
    
    def test_payment_creation(self):
        """Tests payment creation."""
        self.assertEqual(self.payment.appointment, self.appointment)
        self.assertEqual(self.payment.value, 25.00)
        self.assertEqual(self.payment.method, "cash")
        self.assertEqual(self.payment.status, "approved")
    
    def test_payment_str(self):
        """Tests payment string representation."""
        expected = f"Payment {self.payment.id} - {self.appointment}"
        self.assertEqual(str(self.payment), expected)


class ActorCostModelTest(TestCase):
    """Tests for ActorCost model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.cost = ActorCost.objects.create(
            actor=self.actor,
            description="Product purchase",
            value=50.00,
            date=timezone.now().date(),
            category="products"
        )
    
    def test_actor_cost_creation(self):
        """Tests actor cost creation."""
        self.assertEqual(self.cost.actor, self.actor)
        self.assertEqual(self.cost.description, "Product purchase")
        self.assertEqual(self.cost.value, 50.00)
        self.assertEqual(self.cost.category, "products")
    
    def test_actor_cost_str(self):
        """Tests cost string representation."""
        expected = "actor - Product purchase - R$ 50.00"
        self.assertEqual(str(self.cost), expected)


class FinancialReportModelTest(TestCase):
    """Tests for FinancialReport model."""
    
    def setUp(self):
        """Initial setup for tests."""
        self.company = Company.objects.create(
            name="Test Barber Shop",
            cnpj="12.345.678/0001-90"
        )
        
        self.actor = User.objects.create_user(
            username="actor",
            email="actor@example.com",
            password="testpass123",
            role="actor",
            company=self.company
        )
        
        self.report = FinancialReport.objects.create(
            company=self.company,
            actor=self.actor,
            type="complete",
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=30),
            data={"revenues": 1000, "costs": 300, "profit": 700}
        )
    
    def test_report_creation(self):
        """Tests financial report creation."""
        self.assertEqual(self.report.company, self.company)
        self.assertEqual(self.report.actor, self.actor)
        self.assertEqual(self.report.type, "complete")
        self.assertEqual(self.report.data["revenues"], 1000)
    
    def test_report_str(self):
        """Tests report string representation."""
        expected = "Report Complete Report - Test Barber Shop"
        self.assertEqual(str(self.report), expected)
