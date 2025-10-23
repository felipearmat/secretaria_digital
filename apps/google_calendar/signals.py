from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from apps.agendamentos.models import Agendamento
from .models import GoogleCalendarIntegration
from .tasks import (
    sync_agendamento_to_google_calendar,
    remove_agendamento_from_google_calendar
)


@receiver(post_save, sender=Agendamento)
def sync_agendamento_to_google(sender, instance, created, **kwargs):
    """
    Sincroniza agendamento com Google Calendar quando criado ou atualizado.
    """
    # Verifica se a sincronização automática está habilitada
    if not getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
        return
    
    # Verifica se o agendamento deve ser sincronizado
    if instance.status not in ['pendente', 'confirmado']:
        return
    
    # Verifica se o ator tem integração ativa
    try:
        integration = GoogleCalendarIntegration.objects.get(
            usuario=instance.ator,
            sync_enabled=True,
            sync_direction__in=['bidirectional', 'to_google']
        )
    except GoogleCalendarIntegration.DoesNotExist:
        return
    
    # Agenda sincronização
    sync_agendamento_to_google_calendar.delay(instance.id)


@receiver(post_delete, sender=Agendamento)
def remove_agendamento_from_google(sender, instance, **kwargs):
    """
    Remove agendamento do Google Calendar quando excluído.
    """
    # Verifica se a sincronização automática está habilitada
    if not getattr(settings, 'GOOGLE_CALENDAR_AUTO_SYNC', True):
        return
    
    # Verifica se o ator tem integração ativa
    try:
        integration = GoogleCalendarIntegration.objects.get(
            usuario=instance.ator,
            sync_enabled=True,
            sync_direction__in=['bidirectional', 'to_google']
        )
    except GoogleCalendarIntegration.DoesNotExist:
        return
    
    # Agenda remoção
    remove_agendamento_from_google_calendar.delay(instance.id)

