"""
Models for the companies app.
"""

from django.db import models
from django.utils import timezone


class Company(models.Model):
    """Model to represent a company."""
    
    name = models.CharField(max_length=255, verbose_name='Company Name')
    cnpj = models.CharField(
        max_length=18, 
        unique=True, 
        blank=True, 
        null=True,
        verbose_name='CNPJ'
    )
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='Phone'
    )
    email = models.EmailField(
        blank=True, 
        null=True,
        verbose_name='Email'
    )
    address = models.TextField(
        blank=True, 
        null=True,
        verbose_name='Address'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active Company'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created at'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated at'
    )

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def total_users(self):
        """Returns the total number of users in the company."""
        return self.users.count()

    @property
    def total_appointments_today(self):
        """Returns the total number of appointments for today."""
        today = timezone.now().date()
        return self.appointments.filter(
            start_time__date=today,
            status__in=['pending', 'confirmed']
        ).count()
