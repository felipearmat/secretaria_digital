from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from .serializers import (
    GoogleCalendarIntegrationSerializer,
    GoogleCalendarIntegrationCreateSerializer,
    GoogleCalendarEventSerializer,
    GoogleCalendarSyncLogSerializer,
    GoogleCalendarOAuthSerializer,
    GoogleCalendarOAuthCallbackSerializer,
    GoogleCalendarSyncSerializer,
    GoogleCalendarEventCreateSerializer
)
from .services import GoogleCalendarService, GoogleCalendarOAuthService
from .tasks import (
    sync_agendamento_to_google_calendar,
    remove_agendamento_from_google_calendar,
    sync_from_google_calendar,
    sync_all_google_calendar_integrations
)


class GoogleCalendarIntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciar integrações Google Calendar."""
    
    serializer_class = GoogleCalendarIntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra integrações baseado no usuário."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarIntegration.objects.all()
        elif user.is_admin:
            return GoogleCalendarIntegration.objects.filter(
                usuario__empresa=user.empresa
            )
        else:
            return GoogleCalendarIntegration.objects.filter(usuario=user)
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado."""
        if self.action == 'create':
            return GoogleCalendarIntegrationCreateSerializer
        return GoogleCalendarIntegrationSerializer
    
    def perform_create(self, serializer):
        """Cria uma nova integração."""
        serializer.save(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def authorize(self, request, pk=None):
        """Inicia processo de autorização OAuth."""
        integration = self.get_object()
        
        serializer = GoogleCalendarOAuthSerializer(
            data={},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def callback(self, request, pk=None):
        """Processa callback OAuth."""
        integration = self.get_object()
        
        serializer = GoogleCalendarOAuthCallbackSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Sincroniza com Google Calendar."""
        integration = self.get_object()
        
        serializer = GoogleCalendarSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Agenda sincronização
        sync_from_google_calendar.delay(
            integration.id,
            serializer.validated_data['days_back'],
            serializer.validated_data['days_forward']
        )
        
        return Response({
            'message': 'Sincronização agendada com sucesso',
            'integration_id': integration.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Testa conexão com Google Calendar."""
        integration = self.get_object()
        
        try:
            service = GoogleCalendarService(integration)
            # Tenta listar calendários para testar a conexão
            calendar_list = service.service.calendarList().list().execute()
            
            return Response({
                'status': 'success',
                'message': 'Conexão com Google Calendar estabelecida com sucesso',
                'calendars_count': len(calendar_list.get('items', []))
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Erro ao conectar com Google Calendar: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Renova token de acesso."""
        integration = self.get_object()
        
        try:
            service = GoogleCalendarService(integration)
            # O serviço automaticamente renova o token se necessário
            
            return Response({
                'status': 'success',
                'message': 'Token renovado com sucesso',
                'expires_at': integration.token_expires_at
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Erro ao renovar token: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class GoogleCalendarEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar eventos Google Calendar."""
    
    serializer_class = GoogleCalendarEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra eventos baseado no usuário."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarEvent.objects.all()
        elif user.is_admin:
            return GoogleCalendarEvent.objects.filter(
                agendamento__ator__empresa=user.empresa
            )
        else:
            return GoogleCalendarEvent.objects.filter(
                Q(agendamento__ator=user) | Q(agendamento__cliente=user)
            )
    
    @action(detail=False, methods=['post'])
    def create_event(self, request):
        """Cria evento no Google Calendar."""
        serializer = GoogleCalendarEventCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        result = serializer.save()
        
        return Response(result, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def sync_to_google(self, request, pk=None):
        """Sincroniza evento específico para Google Calendar."""
        event = self.get_object()
        
        # Agenda sincronização
        sync_agendamento_to_google_calendar.delay(event.agendamento.id)
        
        return Response({
            'message': 'Sincronização agendada com sucesso',
            'event_id': event.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def remove_from_google(self, request, pk=None):
        """Remove evento do Google Calendar."""
        event = self.get_object()
        
        # Agenda remoção
        remove_agendamento_from_google_calendar.delay(event.agendamento.id)
        
        return Response({
            'message': 'Remoção agendada com sucesso',
            'event_id': event.id
        }, status=status.HTTP_202_ACCEPTED)


class GoogleCalendarSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualizar logs de sincronização."""
    
    serializer_class = GoogleCalendarSyncLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra logs baseado no usuário."""
        user = self.request.user
        
        if user.is_superadmin:
            return GoogleCalendarSyncLog.objects.all()
        elif user.is_admin:
            return GoogleCalendarSyncLog.objects.filter(
                integration__usuario__empresa=user.empresa
            )
        else:
            return GoogleCalendarSyncLog.objects.filter(
                integration__usuario=user
            )
    
    @action(detail=False, methods=['post'])
    def sync_all(self, request):
        """Sincroniza todas as integrações ativas."""
        # Agenda sincronização global
        sync_all_google_calendar_integrations.delay()
        
        return Response({
            'message': 'Sincronização global agendada com sucesso'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Retorna estatísticas de sincronização."""
        queryset = self.get_queryset()
        
        # Estatísticas gerais
        total_syncs = queryset.count()
        successful_syncs = queryset.filter(status='success').count()
        error_syncs = queryset.filter(status='error').count()
        
        # Estatísticas de eventos
        total_events_created = queryset.aggregate(
            total=models.Sum('events_created')
        )['total'] or 0
        
        total_events_updated = queryset.aggregate(
            total=models.Sum('events_updated')
        )['total'] or 0
        
        total_events_deleted = queryset.aggregate(
            total=models.Sum('events_deleted')
        )['total'] or 0
        
        # Última sincronização
        last_sync = queryset.order_by('-started_at').first()
        
        return Response({
            'total_syncs': total_syncs,
            'successful_syncs': successful_syncs,
            'error_syncs': error_syncs,
            'success_rate': (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0,
            'total_events_created': total_events_created,
            'total_events_updated': total_events_updated,
            'total_events_deleted': total_events_deleted,
            'last_sync': GoogleCalendarSyncLogSerializer(last_sync).data if last_sync else None
        }, status=status.HTTP_200_OK)

