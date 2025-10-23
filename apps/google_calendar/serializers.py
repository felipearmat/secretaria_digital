from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import GoogleCalendarIntegration, GoogleCalendarEvent, GoogleCalendarSyncLog
from apps.agendamentos.serializers import AgendamentoSerializer
from apps.autenticacao.serializers import UsuarioSerializer

User = get_user_model()


class GoogleCalendarIntegrationSerializer(serializers.ModelSerializer):
    """Serializer para GoogleCalendarIntegration."""
    
    usuario_nome = serializers.CharField(source='usuario.username', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    is_token_expired = serializers.BooleanField(read_only=True)
    needs_refresh = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = GoogleCalendarIntegration
        fields = [
            'id', 'usuario', 'usuario_nome', 'usuario_email',
            'calendar_id', 'sync_enabled', 'sync_direction',
            'notify_on_create', 'notify_on_update', 'notify_on_delete',
            'is_token_expired', 'needs_refresh', 'last_sync_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_token_expired', 'needs_refresh',
            'last_sync_at', 'created_at', 'updated_at'
        ]
    
    def validate_sync_direction(self, value):
        """Valida a direção de sincronização."""
        valid_directions = ['bidirectional', 'to_google', 'from_google']
        if value not in valid_directions:
            raise serializers.ValidationError(
                f"Direção deve ser uma das opções: {', '.join(valid_directions)}"
            )
        return value


class GoogleCalendarIntegrationCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de integração Google Calendar."""
    
    class Meta:
        model = GoogleCalendarIntegration
        fields = [
            'calendar_id', 'sync_enabled', 'sync_direction',
            'notify_on_create', 'notify_on_update', 'notify_on_delete'
        ]
    
    def create(self, validated_data):
        """Cria uma nova integração."""
        user = self.context['request'].user
        validated_data['usuario'] = user
        return super().create(validated_data)


class GoogleCalendarEventSerializer(serializers.ModelSerializer):
    """Serializer para GoogleCalendarEvent."""
    
    agendamento_data = AgendamentoSerializer(source='agendamento', read_only=True)
    cliente_nome = serializers.CharField(source='agendamento.cliente.username', read_only=True)
    ator_nome = serializers.CharField(source='agendamento.ator.username', read_only=True)
    servico_nome = serializers.CharField(source='agendamento.servico.nome', read_only=True)
    
    class Meta:
        model = GoogleCalendarEvent
        fields = [
            'id', 'agendamento', 'agendamento_data',
            'google_event_id', 'google_calendar_id',
            'sync_status', 'sync_error',
            'cliente_nome', 'ator_nome', 'servico_nome',
            'created_at', 'updated_at', 'last_sync_at'
        ]
        read_only_fields = [
            'id', 'agendamento_data', 'cliente_nome', 'ator_nome', 'servico_nome',
            'created_at', 'updated_at', 'last_sync_at'
        ]


class GoogleCalendarSyncLogSerializer(serializers.ModelSerializer):
    """Serializer para GoogleCalendarSyncLog."""
    
    integration_usuario = serializers.CharField(
        source='integration.usuario.username', 
        read_only=True
    )
    duration_display = serializers.SerializerMethodField()
    events_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = GoogleCalendarSyncLog
        fields = [
            'id', 'integration', 'integration_usuario',
            'sync_type', 'status', 'error_message',
            'events_created', 'events_updated', 'events_deleted', 'events_conflicted',
            'events_summary', 'started_at', 'completed_at', 'duration_display'
        ]
        read_only_fields = [
            'id', 'integration_usuario', 'events_summary', 'duration_display',
            'started_at', 'completed_at'
        ]
    
    def get_duration_display(self, obj):
        """Retorna a duração formatada."""
        if obj.duration_seconds:
            if obj.duration_seconds < 60:
                return f"{obj.duration_seconds}s"
            elif obj.duration_seconds < 3600:
                minutes = obj.duration_seconds // 60
                seconds = obj.duration_seconds % 60
                return f"{minutes}m {seconds}s"
            else:
                hours = obj.duration_seconds // 3600
                minutes = (obj.duration_seconds % 3600) // 60
                return f"{hours}h {minutes}m"
        return "-"
    
    def get_events_summary(self, obj):
        """Retorna resumo dos eventos processados."""
        total = obj.events_created + obj.events_updated + obj.events_deleted
        return f"{total} eventos ({obj.events_created}C, {obj.events_updated}U, {obj.events_deleted}D)"


class GoogleCalendarOAuthSerializer(serializers.Serializer):
    """Serializer para OAuth do Google Calendar."""
    
    authorization_url = serializers.URLField(read_only=True)
    state = serializers.CharField(max_length=255, required=False)
    
    def create(self, validated_data):
        """Cria URL de autorização OAuth."""
        from .services import GoogleCalendarOAuthService
        
        user = self.context['request'].user
        authorization_url = GoogleCalendarOAuthService.get_authorization_url(user)
        
        return {
            'authorization_url': authorization_url
        }


class GoogleCalendarOAuthCallbackSerializer(serializers.Serializer):
    """Serializer para callback OAuth do Google Calendar."""
    
    code = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=255, required=False)
    
    def validate(self, attrs):
        """Valida os dados do callback."""
        if not attrs.get('code'):
            raise serializers.ValidationError("Código de autorização é obrigatório")
        return attrs
    
    def create(self, validated_data):
        """Processa o callback OAuth."""
        from .services import GoogleCalendarOAuthService
        
        user = self.context['request'].user
        code = validated_data['code']
        
        # Simula a URL de callback completa
        authorization_response = f"http://localhost:8000/google-calendar/callback/?code={code}"
        
        integration = GoogleCalendarOAuthService.handle_authorization_callback(
            user, authorization_response
        )
        
        return GoogleCalendarIntegrationSerializer(integration).data


class GoogleCalendarSyncSerializer(serializers.Serializer):
    """Serializer para sincronização com Google Calendar."""
    
    sync_type = serializers.ChoiceField(
        choices=[
            ('full', 'Sincronização Completa'),
            ('incremental', 'Sincronização Incremental'),
            ('manual', 'Sincronização Manual'),
        ],
        default='manual'
    )
    days_back = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=30,
        help_text="Número de dias para buscar no passado"
    )
    days_forward = serializers.IntegerField(
        min_value=1,
        max_value=365,
        default=365,
        help_text="Número de dias para buscar no futuro"
    )
    
    def validate(self, attrs):
        """Valida os dados de sincronização."""
        if attrs['days_back'] + attrs['days_forward'] > 400:
            raise serializers.ValidationError(
                "A soma dos dias não pode ser maior que 400"
            )
        return attrs


class GoogleCalendarEventCreateSerializer(serializers.Serializer):
    """Serializer para criar evento no Google Calendar."""
    
    agendamento_id = serializers.IntegerField()
    
    def validate_agendamento_id(self, value):
        """Valida se o agendamento existe e pertence ao usuário."""
        from apps.agendamentos.models import Agendamento
        
        try:
            agendamento = Agendamento.objects.get(id=value)
        except Agendamento.DoesNotExist:
            raise serializers.ValidationError("Agendamento não encontrado")
        
        # Verifica se o usuário tem permissão
        user = self.context['request'].user
        if not (user == agendamento.ator or user.is_admin or user.is_superadmin):
            raise serializers.ValidationError("Você não tem permissão para este agendamento")
        
        return value
    
    def create(self, validated_data):
        """Cria evento no Google Calendar."""
        from .services import GoogleCalendarService
        from apps.agendamentos.models import Agendamento
        
        agendamento = Agendamento.objects.get(id=validated_data['agendamento_id'])
        user = self.context['request'].user
        
        # Busca a integração do usuário
        try:
            integration = GoogleCalendarIntegration.objects.get(
                usuario=user,
                sync_enabled=True
            )
        except GoogleCalendarIntegration.DoesNotExist:
            raise serializers.ValidationError(
                "Integração com Google Calendar não encontrada ou desabilitada"
            )
        
        # Cria o serviço e o evento
        service = GoogleCalendarService(integration)
        google_event = service.create_event(agendamento)
        
        return GoogleCalendarEventSerializer(google_event).data

