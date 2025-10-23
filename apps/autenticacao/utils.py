"""
Utility functions for authentication app.
"""

from django.contrib.auth import get_user_model

User = get_user_model()


def can_translate(user):
    """
    Check if user can access translation interface.
    Only superusers and admins can translate.
    """
    if not user or not user.is_authenticated:
        return False
    
    return user.is_superuser or user.is_admin
