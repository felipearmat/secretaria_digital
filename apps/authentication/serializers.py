"""
Serializers for the authentication app.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'company', 'is_active', 'created_at',
            'updated_at', 'last_login', 'date_joined'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_login', 'date_joined'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user creation."""
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone', 'role', 'company', 'is_active', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        """Validates if passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs
    
    def create(self, validated_data):
        """Creates a new user."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login."""
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Validates user credentials."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('Inactive user.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Username and password are required.')
