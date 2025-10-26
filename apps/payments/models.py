"""
Models for the payments app.
"""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from apps.authentication.models import User
from apps.companies.models import Company
from apps.appointments.models import Appointment, Service


class Coupon(models.Model):
    """Model to represent discount coupons."""
    
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage'),
        ('fixed_value', 'Fixed Value'),
    )

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Coupon Code'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="coupons",
        verbose_name='Company'
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupons",
        null=True,
        blank=True,
        verbose_name='Actor/Provider'
    )
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        verbose_name='Discount Type'
    )
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Discount Value'
    )
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')
    max_uses = models.PositiveIntegerField(
        default=1,
        verbose_name='Maximum Uses'
    )
    max_uses_per_client = models.PositiveIntegerField(
        default=1,
        verbose_name='Maximum Uses per Client'
    )
    services = models.ManyToManyField(
        Service,
        blank=True,
        verbose_name='Valid Services'
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Active Coupon'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.company.name}"

    def is_valid(self):
        """Checks if the coupon is valid."""
        today = timezone.now().date()
        return (
            self.active and
            self.start_date <= today <= self.end_date and
            self.uses.count() < self.max_uses
        )

    def can_be_used_by(self, client):
        """Checks if the coupon can be used by a specific client."""
        if not self.is_valid():
            return False
        
        client_uses = self.uses.filter(client=client).count()
        return client_uses < self.max_uses_per_client

    def calculate_discount(self, original_value):
        """Calculates the discount value."""
        if self.discount_type == 'percentage':
            return original_value * (self.discount_value / 100)
        else:
            return min(self.discount_value, original_value)


class CouponUsage(models.Model):
    """Model to track coupon usage."""
    
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name="uses",
        verbose_name='Coupon'
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="coupon_uses",
        verbose_name='Client'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="coupon_uses",
        verbose_name='Appointment'
    )
    discount_value_applied = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Applied Discount Value'
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Used at'
    )

    class Meta:
        verbose_name = 'Coupon Usage'
        verbose_name_plural = 'Coupon Usages'
        ordering = ['-used_at']
        unique_together = ['coupon', 'appointment']

    def __str__(self):
        return f"{self.coupon.code} - {self.client.username}"


class Payment(models.Model):
    """Model to represent payments."""
    
    METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name='Appointment'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Value'
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name='Payment Method'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Payment Date'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.id} - {self.appointment}"


class ActorCost(models.Model):
    """Model to represent actor costs."""
    
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="costs",
        verbose_name='Actor/Provider'
    )
    description = models.CharField(
        max_length=255,
        verbose_name='Cost Description'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Value'
    )
    date = models.DateField(
        default=timezone.now,
        verbose_name='Date'
    )
    category = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Category'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notes'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="costs_created",
        verbose_name='Created by'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Actor Cost'
        verbose_name_plural = 'Actor Costs'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.actor.username} - {self.description} - R$ {self.value}"


class FinancialReport(models.Model):
    """Model to store generated financial reports."""
    
    REPORT_TYPE_CHOICES = (
        ('revenue', 'Revenue'),
        ('costs', 'Costs'),
        ('profit', 'Profit'),
        ('complete', 'Complete Report'),
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name='Company'
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True,
        verbose_name='Actor/Provider'
    )
    type = models.CharField(
        max_length=20,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='Report Type'
    )
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')
    data = models.JSONField(verbose_name='Report Data')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )

    class Meta:
        verbose_name = 'Financial Report'
        verbose_name_plural = 'Financial Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.get_type_display()} - {self.company.name}"
