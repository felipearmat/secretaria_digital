"""
Views para o app de notificações.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Notificacao, ConfiguracaoNotificacao, TemplateNotificacao
from .serializers import (
    NotificacaoSerializer, ConfiguracaoNotificacaoSerializer,
    TemplateNotificacaoSerializer
)


class NotificacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar notificações."""
    
    queryset = Notificacao.objects.all()
    serializer_class = NotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra notificações baseado no usuário logado."""
        return Notificacao.objects.filter(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def marcar_como_lida(self, request, pk=None):
        """Marca uma notificação como lida."""
        notificacao = self.get_object()
        notificacao.marcar_como_lida()
        return Response({'status': 'Notificação marcada como lida'})
    
    @action(detail=False, methods=['post'])
    def marcar_todas_como_lidas(self, request):
        """Marca todas as notificações do usuário como lidas."""
        notificacoes = self.get_queryset().filter(lida=False)
        notificacoes.update(lida=True, data_leitura=timezone.now())
        return Response({'status': 'Todas as notificações foram marcadas como lidas'})
    
    @action(detail=False, methods=['get'])
    def nao_lidas(self, request):
        """Retorna notificações não lidas."""
        notificacoes = self.get_queryset().filter(lida=False)
        serializer = self.get_serializer(notificacoes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def contador(self, request):
        """Retorna contador de notificações não lidas."""
        count = self.get_queryset().filter(lida=False).count()
        return Response({'count': count})


class ConfiguracaoNotificacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar configurações de notificação."""
    
    queryset = ConfiguracaoNotificacao.objects.all()
    serializer_class = ConfiguracaoNotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra configurações baseado no usuário logado."""
        return ConfiguracaoNotificacao.objects.filter(usuario=self.request.user)
    
    def perform_create(self, serializer):
        """Define o usuário da configuração."""
        serializer.save(usuario=self.request.user)


class TemplateNotificacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar templates de notificação."""
    
    queryset = TemplateNotificacao.objects.all()
    serializer_class = TemplateNotificacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra templates baseado no usuário logado."""
        user = self.request.user
        
        if user.is_superadmin:
            return TemplateNotificacao.objects.all()
        else:
            return TemplateNotificacao.objects.filter(ativo=True)
