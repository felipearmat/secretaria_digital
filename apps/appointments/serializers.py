"""
Serializers for the appointments app.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Service, Appointment, Recurrence, Block
from apps.authentication.serializers import UserSerializer
from apps.companies.serializers import CompanySerializer


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for the Service model."""
    
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'duration_minutes', 'base_price',
            'company', 'actor', 'is_active', 'created_at', 'actor_name', 'company_name'
        ]
        read_only_fields = ['id', 'created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model."""
    
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'client', 'actor', 'service', 'start_time', 'end_time', 'status',
            'notes', 'final_price', 'created_at', 'updated_at',
            'client_name', 'actor_name', 'service_name'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments."""
    
    class Meta:
        model = Appointment
        fields = [
            'client', 'actor', 'service', 'start_time', 'end_time',
            'notes', 'final_price'
        ]
    
    def validate(self, attrs):
        """Validates the appointment."""
        # Check if the actor can be scheduled
        actor = attrs.get('actor')
        if actor and not actor.is_actor:
            raise serializers.ValidationError("The selected user is not an actor.")
        
        # Check if the service belongs to the actor
        service = attrs.get('service')
        if service and actor and service.actor != actor:
            raise serializers.ValidationError("The service does not belong to the selected actor.")
        
        # Time validations
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time:
            if start_time >= end_time:
                raise serializers.ValidationError(
                    "The start date/time must be before the end date/time."
                )
            
            # Check if it's not in the past
            if start_time < timezone.now():
                raise serializers.ValidationError(
                    "Cannot schedule in the past."
                )
            
            # Check for conflicts with other appointments
            if actor:
                conflicts = Appointment.objects.filter(
                    actor=actor,
                    status__in=['pending', 'confirmed'],
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                
                if conflicts.exists():
                    raise serializers.ValidationError(
                        "There is already an appointment at this time for this actor."
                    )
            
            # Check for conflicts with blocks
            if actor:
                from .models import Block
                blocks = Block.objects.filter(
                    actor=actor,
                    is_active=True,
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                
                if blocks.exists():
                    raise serializers.ValidationError(
                        f"This time is blocked: {blocks.first().title}"
                    )
        
        return attrs


class RecurrenceSerializer(serializers.ModelSerializer):
    """Serializer for the Recurrence model."""
    
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    
    class Meta:
        model = Recurrence
        fields = [
            'id', 'actor', 'start_time', 'end_time', 'frequency', 'weekday',
            'day_of_month', 'start_date', 'end_date', 'is_active', 'created_at', 'actor_name'
        ]
        read_only_fields = ['id', 'created_at']


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for the Block model."""
    
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)
    
    class Meta:
        model = Block
        fields = [
            'id', 'actor', 'title', 'description', 'block_type', 'start_time',
            'end_time', 'is_active', 'created_at', 'actor_name'
        ]
        read_only_fields = ['id', 'created_at']
