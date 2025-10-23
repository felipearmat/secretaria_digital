"""
Celery tasks for the appointments app.
"""

from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta, date
from .models import Recurrence, Appointment, Block


@shared_task(queue='low')
def low_priority_generate_recurring_appointments():
    """
    Generates appointments based on active recurrences.
    """
    today = timezone.now().date()
    appointments_created = 0
    
    # Find active recurrences
    recurrences = Recurrence.objects.filter(
        is_active=True,
        start_date__lte=today
    )
    
    for recurrence in recurrences:
        # Check if recurrence is still valid
        if recurrence.end_date and recurrence.end_date < today:
            continue
        
        # Generate appointments based on frequency
        if recurrence.frequency == 'daily':
            appointments_created += _generate_daily_appointments(recurrence, today)
        elif recurrence.frequency == 'weekly':
            appointments_created += _generate_weekly_appointments(recurrence, today)
        elif recurrence.frequency == 'monthly':
            appointments_created += _generate_monthly_appointments(recurrence, today)
    
    return f"Generated {appointments_created} recurring appointments"


def _generate_daily_appointments(recurrence, start_date):
    """Generates daily appointments."""
    appointments_created = 0
    current_date = max(recurrence.start_date, start_date)
    end_date = recurrence.end_date or (current_date + timedelta(days=30))
    
    while current_date <= end_date:
        # Check if there's no block on this day
        if not _check_block(recurrence.actor, current_date, recurrence.start_time, recurrence.end_time):
            # Verifica se já existe agendamento neste horário
            if not _verificar_agendamento_existente(recorrência.ator, data_atual, recorrência.inicio, recorrência.fim):
                _criar_agendamento_recorrente(recorrência, data_atual)
                agendamentos_criados += 1
        
        data_atual += timedelta(days=1)
    
    return agendamentos_criados


def _gerar_agendamentos_semanais(recorrência, data_inicio):
    """Gera agendamentos semanais."""
    agendamentos_criados = 0
    data_atual = max(recorrência.data_inicio, data_inicio)
    data_fim = recorrência.data_fim or (data_atual + timedelta(days=30))
    
    # Encontra a próxima data com o dia da semana correto
    while data_atual.weekday() != recorrência.dia_semana:
        data_atual += timedelta(days=1)
    
    while data_atual <= data_fim:
        # Verifica se não há bloqueio neste dia
        if not _verificar_bloqueio(recorrência.ator, data_atual, recorrência.inicio, recorrência.fim):
            # Verifica se já existe agendamento neste horário
            if not _verificar_agendamento_existente(recorrência.ator, data_atual, recorrência.inicio, recorrência.fim):
                _criar_agendamento_recorrente(recorrência, data_atual)
                agendamentos_criados += 1
        
        data_atual += timedelta(days=7)
    
    return agendamentos_criados


def _gerar_agendamentos_mensais(recorrência, data_inicio):
    """Gera agendamentos mensais."""
    agendamentos_criados = 0
    data_atual = max(recorrência.data_inicio, data_inicio)
    data_fim = recorrência.data_fim or (data_atual + timedelta(days=90))
    
    # Encontra a próxima data com o dia do mês correto
    while data_atual.day != recorrência.dia_mes:
        data_atual += timedelta(days=1)
        if data_atual.day == 1:  # Próximo mês
            data_atual = data_atual.replace(day=recorrência.dia_mes)
    
    while data_atual <= data_fim:
        # Verifica se não há bloqueio neste dia
        if not _verificar_bloqueio(recorrência.ator, data_atual, recorrência.inicio, recorrência.fim):
            # Verifica se já existe agendamento neste horário
            if not _verificar_agendamento_existente(recorrência.ator, data_atual, recorrência.inicio, recorrência.fim):
                _criar_agendamento_recorrente(recorrência, data_atual)
                agendamentos_criados += 1
        
        # Próximo mês
        if data_atual.month == 12:
            data_atual = data_atual.replace(year=data_atual.year + 1, month=1, day=recorrência.dia_mes)
        else:
            data_atual = data_atual.replace(month=data_atual.month + 1, day=recorrência.dia_mes)
    
    return agendamentos_criados


def _verificar_bloqueio(ator, data, hora_inicio, hora_fim):
    """Verifica se há bloqueio no horário especificado."""
    inicio_datetime = datetime.combine(data, hora_inicio)
    fim_datetime = datetime.combine(data, hora_fim)
    
    bloqueios = Bloqueio.objects.filter(
        ator=ator,
        ativo=True,
        inicio__lt=fim_datetime,
        fim__gt=inicio_datetime
    )
    
    return bloqueios.exists()


def _verificar_agendamento_existente(ator, data, hora_inicio, hora_fim):
    """Verifica se já existe agendamento no horário especificado."""
    inicio_datetime = datetime.combine(data, hora_inicio)
    fim_datetime = datetime.combine(data, hora_fim)
    
    agendamentos = Agendamento.objects.filter(
        ator=ator,
        status__in=['pendente', 'confirmado'],
        inicio__lt=fim_datetime,
        fim__gt=inicio_datetime
    )
    
    return agendamentos.exists()


def _criar_agendamento_recorrente(recorrência, data):
    """Cria um agendamento baseado na recorrência."""
    inicio_datetime = datetime.combine(data, recorrência.inicio)
    fim_datetime = datetime.combine(data, recorrência.fim)
    
    # Cria um agendamento "bloqueado" (não disponível para clientes)
    agendamento = Agendamento.objects.create(
        ator=recorrência.ator,
        cliente=recorrência.ator,  # Auto-agendamento
        servico=None,  # Será definido quando necessário
        inicio=inicio_datetime,
        fim=fim_datetime,
        status='confirmado',
        observacoes=f'Agendamento recorrente - {recorrência.get_frequencia_display()}'
    )
    
    return agendamento


@shared_task(queue='high')
def high_priority_validar_conflitos_agendamento(agendamento_id):
    """
    Valida conflitos de um agendamento específico.
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        # Verifica conflitos com outros agendamentos
        conflitos = Agendamento.objects.filter(
            ator=agendamento.ator,
            status__in=['pendente', 'confirmado'],
            inicio__lt=agendamento.fim,
            fim__gt=agendamento.inicio
        ).exclude(id=agendamento.id)
        
        if conflitos.exists():
            # Cancela o agendamento se houver conflito
            agendamento.status = 'cancelado'
            agendamento.observacoes = f"Cancelado por conflito: {conflitos.first().id}"
            agendamento.save()
            
            return f"Agendamento {agendamento_id} cancelado por conflito"
        
        # Verifica conflitos com bloqueios
        bloqueios = Bloqueio.objects.filter(
            ator=agendamento.ator,
            ativo=True,
            inicio__lt=agendamento.fim,
            fim__gt=agendamento.inicio
        )
        
        if bloqueios.exists():
            agendamento.status = 'cancelado'
            agendamento.observacoes = f"Cancelado por bloqueio: {bloqueios.first().titulo}"
            agendamento.save()
            
            return f"Agendamento {agendamento_id} cancelado por bloqueio"
        
        return f"Agendamento {agendamento_id} validado com sucesso"
        
    except Agendamento.DoesNotExist:
        return f"Agendamento {agendamento_id} não encontrado"


@shared_task(queue='low')
def low_priority_limpar_agendamentos_antigos():
    """
    Remove agendamentos antigos e cancelados.
    """
    data_limite = timezone.now().date() - timedelta(days=90)
    
    agendamentos_removidos = Agendamento.objects.filter(
        inicio__date__lt=data_limite,
        status__in=['cancelado', 'finalizado']
    ).delete()[0]
    
    return f"Removidos {agendamentos_removidos} agendamentos antigos"
