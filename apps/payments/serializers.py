"""
Serializers for the payments app.
"""

from rest_framework import serializers
from .models import Coupon, CouponUsage, Payment, ActorCost, FinancialReport
from apps.appointments.serializers import AppointmentSerializer
from apps.authentication.serializers import UserSerializer
from apps.companies.serializers import CompanySerializer


class CouponSerializer(serializers.ModelSerializer):
    """Serializer for the Coupon model."""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    services_names = serializers.StringRelatedField(source='services', many=True, read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'company', 'actor', 'discount_type', 'discount_value',
            'start_date', 'end_date', 'max_uses', 'max_uses_per_client',
            'services', 'active', 'created_at', 'company_name', 'actor_name', 'services_names'
        ]
        read_only_fields = ['id', 'created_at']


class CouponUsageSerializer(serializers.ModelSerializer):
    """Serializer for the CouponUsage model."""
    
    coupon_code = serializers.CharField(source='coupon.code', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    
    class Meta:
        model = CouponUsage
        fields = [
            'id', 'coupon', 'client', 'appointment', 'discount_value_applied',
            'used_at', 'coupon_code', 'client_name'
        ]
        read_only_fields = ['id', 'used_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model."""
    
    appointment_info = AppointmentSerializer(source='appointment', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'appointment', 'value', 'method', 'status', 'notes',
            'payment_date', 'created_at', 'appointment_info'
        ]
        read_only_fields = ['id', 'created_at']


class ActorCostSerializer(serializers.ModelSerializer):
    """Serializer for the ActorCost model."""
    
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ActorCost
        fields = [
            'id', 'actor', 'description', 'value', 'date', 'category',
            'notes', 'created_by', 'created_at', 'actor_name', 'created_by_name'
        ]
        read_only_fields = ['id', 'created_at']


class FinancialReportSerializer(serializers.ModelSerializer):
    """Serializer for the FinancialReport model."""
    
    company_name = serializers.CharField(source='company.name', read_only=True)
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    
    class Meta:
        model = FinancialReport
        fields = [
            'id', 'company', 'actor', 'type', 'start_date', 'end_date',
            'data', 'created_at', 'company_name', 'actor_name'
        ]
        read_only_fields = ['id', 'created_at']
