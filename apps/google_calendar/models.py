from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.agendamentos.models import Agendamento
from apps.autenticacao.models import Usuario

User = get_user_model()


class GoogleCalendarIntegration(models.Model):
    """
    Modelo para armazenar as configurações de integração com Google Calendar
    de cada usuário/ator.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='google_calendar_integration',
        verbose_name='Usuário'
    )
    
    # Credenciais OAuth
    access_token = models.TextField(
        verbose_name='Access Token',
        help_text='Token de acesso do Google OAuth'
    )
    refresh_token = models.TextField(
        verbose_name='Refresh Token',
        help_text='Token de renovação do Google OAuth'
    )
    token_expires_at = models.DateTimeField(
        verbose_name='Token Expira Em',
        help_text='Data e hora de expiração do token'
    )
    
    # Configurações de sincronização
    calendar_id = models.CharField(
        max_length=255,
        verbose_name='ID do Calendário',
        help_text='ID do calendário do Google Calendar',
        default='primary'
    )
    sync_enabled = models.BooleanField(
        default=True,
        verbose_name='Sincronização Habilitada',
        help_text='Se a sincronização com Google Calendar está ativa'
    )
    sync_direction = models.CharField(
        max_length=20,
        choices=[
            ('bidirectional', 'Bidirecional'),
            ('to_google', 'Para Google'),
            ('from_google', 'Do Google'),
        ],
        default='bidirectional',
        verbose_name='Direção da Sincronização',
        help_text='Direção da sincronização dos eventos'
    )
    
    # Configurações de notificação
    notify_on_create = models.BooleanField(
        default=True,
        verbose_name='Notificar ao Criar',
        help_text='Enviar notificação quando criar evento no Google Calendar'
    )
    notify_on_update = models.BooleanField(
        default=True,
        verbose_name='Notificar ao Atualizar',
        help_text='Enviar notificação quando atualizar evento no Google Calendar'
    )
    notify_on_delete = models.BooleanField(
        default=True,
        verbose_name='Notificar ao Excluir',
        help_text='Enviar notificação quando excluir evento no Google Calendar'
    )
    
    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Sincronização',
        help_text='Data e hora da última sincronização'
    )
    
    class Meta:
        verbose_name = 'Integração Google Calendar'
        verbose_name_plural = 'Integrações Google Calendar'
        db_table = 'google_calendar_integration'
    
    def __str__(self):
        return f"Google Calendar - {self.usuario.username}"
    
    @property
    def is_token_expired(self):
        """Verifica se o token de acesso expirou."""
        if not self.token_expires_at:
            return True
        return timezone.now() >= self.token_expires_at
    
    def needs_refresh(self):
        """Verifica se o token precisa ser renovado."""
        if not self.token_expires_at:
            return True
        # Renova se expira em menos de 5 minutos
        return timezone.now() >= (self.token_expires_at - timezone.timedelta(minutes=5))


class GoogleCalendarEvent(models.Model):
    """
    Modelo para armazenar o mapeamento entre agendamentos e eventos do Google Calendar.
    """
    agendamento = models.OneToOneField(
        Agendamento,
        on_delete=models.CASCADE,
        related_name='google_calendar_event',
        verbose_name='Agendamento'
    )
    
    # IDs do Google Calendar
    google_event_id = models.CharField(
        max_length=255,
        verbose_name='ID do Evento Google',
        help_text='ID do evento no Google Calendar'
    )
    google_calendar_id = models.CharField(
        max_length=255,
        verbose_name='ID do Calendário Google',
        help_text='ID do calendário onde o evento foi criado'
    )
    
    # Status de sincronização
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('synced', 'Sincronizado'),
            ('pending', 'Pendente'),
            ('error', 'Erro'),
            ('conflict', 'Conflito'),
        ],
        default='synced',
        verbose_name='Status da Sincronização'
    )
    sync_error = models.TextField(
        blank=True,
        null=True,
        verbose_name='Erro de Sincronização',
        help_text='Mensagem de erro em caso de falha na sincronização'
    )
    
    # Metadados
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Criado em'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Atualizado em'
    )
    last_sync_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Sincronização'
    )
    
    class Meta:
        verbose_name = 'Evento Google Calendar'
        verbose_name_plural = 'Eventos Google Calendar'
        db_table = 'google_calendar_event'
        unique_together = ['google_event_id', 'google_calendar_id']
    
    def __str__(self):
        return f"Google Event {self.google_event_id} - {self.agendamento}"


class GoogleCalendarSyncLog(models.Model):
    """
    Modelo para armazenar logs de sincronização com Google Calendar.
    """
    integration = models.ForeignKey(
        GoogleCalendarIntegration,
        on_delete=models.CASCADE,
        related_name='sync_logs',
        verbose_name='Integração'
    )
    
    # Detalhes da sincronização
    sync_type = models.CharField(
        max_length=20,
        choices=[
            ('full', 'Sincronização Completa'),
            ('incremental', 'Sincronização Incremental'),
            ('manual', 'Sincronização Manual'),
            ('automatic', 'Sincronização Automática'),
        ],
        verbose_name='Tipo de Sincronização'
    )
    
    # Resultados
    events_created = models.PositiveIntegerField(
        default=0,
        verbose_name='Eventos Criados'
    )
    events_updated = models.PositiveIntegerField(
        default=0,
        verbose_name='Eventos Atualizados'
    )
    events_deleted = models.PositiveIntegerField(
        default=0,
        verbose_name='Eventos Excluídos'
    )
    events_conflicted = models.PositiveIntegerField(
        default=0,
        verbose_name='Eventos em Conflito'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Sucesso'),
            ('error', 'Erro'),
            ('partial', 'Parcial'),
        ],
        verbose_name='Status'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensagem de Erro'
    )
    
    # Metadados
    started_at = models.DateTimeField(
        verbose_name='Iniciado em'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Concluído em'
    )
    duration_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Duração (segundos)'
    )
    
    class Meta:
        verbose_name = 'Log de Sincronização Google Calendar'
        verbose_name_plural = 'Logs de Sincronização Google Calendar'
        db_table = 'google_calendar_sync_log'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Sync Log {self.id} - {self.integration.usuario.username}"
    
    def save(self, *args, **kwargs):
        if self.completed_at and self.started_at:
            self.duration_seconds = int((self.completed_at - self.started_at).total_seconds())
        super().save(*args, **kwargs)

