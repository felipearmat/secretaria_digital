"""
Admin configuration for the authentication app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for the User model."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'role', 'company', 'is_active', 'is_staff', 'created_at'
    ]
    list_filter = [
        'role', 'is_active', 'is_staff', 'is_superuser', 
        'company', 'created_at'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Permissions and Roles', {
            'fields': (
                'role', 'company', 'is_active', 'is_staff', 
                'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 
                'role', 'company', 'is_active'
            ),
        }),
    )
    
    def get_queryset(self, request):
        """Filters users based on the logged-in user."""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        elif request.user.is_admin:
            return qs.filter(company=request.user.company)
        else:
            return qs.filter(id=request.user.id)
