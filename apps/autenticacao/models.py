"""
Models for the authentication app.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.empresas.models import Empresa


class User(AbstractUser):
    """Custom user model with roles and company."""
    
    ROLE_CHOICES = (
        ('superadmin', 'Super Administrator'),
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('actor', 'Actor/Service Provider'),
        ('user', 'User'),
    )
    
    company = models.ForeignKey(
        'empresas.Company',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name='Company'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Phone'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Role'
    )
    google_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Google ID'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active User'
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
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_superadmin(self):
        """Checks if the user is a super administrator."""
        return self.role == 'superadmin'

    @property
    def is_admin(self):
        """Checks if the user is an administrator."""
        return self.role in ['superadmin', 'admin']

    @property
    def is_manager(self):
        """Checks if the user is a manager or higher."""
        return self.role in ['superadmin', 'admin', 'gerente']

    @property
    def is_actor(self):
        """Checks if the user is an actor or higher."""
        return self.role in ['superadmin', 'admin', 'gerente', 'ator']

    def can_manage_company(self, company):
        """Checks if the user can manage a specific company."""
        if self.is_superadmin:
            return True
        return self.company == company and self.is_admin

    def can_manage_actors(self, company):
        """Checks if the user can manage actors of a company."""
        if self.is_superadmin:
            return True
        return self.company == company and self.is_manager

    def can_create_appointments(self, company):
        """Checks if the user can create appointments."""
        if self.is_superadmin:
            return True
        return self.company == company and self.is_actor
