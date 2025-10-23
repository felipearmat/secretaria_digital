"""
Configuração do admin para o app de autenticação.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin customizado para o modelo Usuario."""
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'role', 'empresa', 'ativo', 'is_staff', 'criado_em'
    ]
    list_filter = [
        'role', 'ativo', 'is_staff', 'is_superuser', 
        'empresa', 'criado_em'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    readonly_fields = ['criado_em', 'atualizado_em', 'last_login', 'date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'email', 'telefone')
        }),
        ('Permissões e Papéis', {
            'fields': (
                'role', 'empresa', 'ativo', 'is_active', 'is_staff', 
                'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'date_joined', 'criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 
                'role', 'empresa', 'ativo'
            ),
        }),
    )
    
    def get_queryset(self, request):
        """Filtra usuários baseado no usuário logado."""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        elif request.user.is_admin:
            return qs.filter(empresa=request.user.empresa)
        else:
            return qs.filter(id=request.user.id)
