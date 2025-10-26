"""
Serializers for the companies app.
"""

from rest_framework import serializers
from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for the Company model."""
    
    total_users = serializers.ReadOnlyField()
    total_appointments_today = serializers.ReadOnlyField()
    
    class Meta:
        model = Company
        fields = [
            'id', 'name', 'cnpj', 'phone', 'email', 'address', 
            'is_active', 'created_at', 'updated_at', 'total_users', 
            'total_appointments_today'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
