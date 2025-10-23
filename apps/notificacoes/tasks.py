"""
Tasks do Celery para o app de notificações.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Notificacao, ConfiguracaoNotificacao, TemplateNotificacao
from apps.agendamentos.models import Agendamento
from apps.autenticacao.models import Usuario


@shared_task(queue='high')
def high_priority_enviar_notificacao_agendamento(agendamento_id, tipo_notificacao):
    """
    Envia notificação de alta prioridade para agendamentos.
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        # Cria notificação para o cliente
        Notificacao.objects.create(
            usuario=agendamento.cliente,
            titulo=f"Agendamento {tipo_notificacao}",
            mensagem=f"Seu agendamento para {agendamento.servico.nome} foi {tipo_notificacao}.",
            tipo=f'agendamento_{tipo_notificacao}',
            prioridade='alta',
            agendamento=agendamento
        )
        
        # Cria notificação para o ator
        Notificacao.objects.create(
            usuario=agendamento.ator,
            titulo=f"Agendamento {tipo_notificacao}",
            mensagem=f"Agendamento com {agendamento.cliente.get_full_name()} foi {tipo_notificacao}.",
            tipo=f'agendamento_{tipo_notificacao}',
            prioridade='alta',
            agendamento=agendamento
        )
        
        return f"Notificações enviadas para agendamento {agendamento_id}"
        
    except Agendamento.DoesNotExist:
        return f"Agendamento {agendamento_id} não encontrado"


@shared_task(queue='low')
def low_priority_enviar_lembrete_agendamento(agendamento_id):
    """
    Envia lembrete de agendamento (baixa prioridade).
    """
    try:
        agendamento = Agendamento.objects.get(id=agendamento_id)
        
        # Verifica se o agendamento ainda está ativo
        if agendamento.status not in ['pendente', 'confirmado']:
            return f"Agendamento {agendamento_id} não está ativo"
        
        # Cria notificação de lembrete
        Notificacao.objects.create(
            usuario=agendamento.cliente,
            titulo="Lembrete de Agendamento",
            mensagem=f"Lembrete: Você tem um agendamento amanhã às {agendamento.inicio.strftime('%H:%M')}.",
            tipo='lembrete',
            prioridade='media',
            agendamento=agendamento
        )
        
        return f"Lembrete enviado para agendamento {agendamento_id}"
        
    except Agendamento.DoesNotExist:
        return f"Agendamento {agendamento_id} não encontrado"


@shared_task(queue='low')
def low_priority_processar_lembretes_diarios():
    """
    Processa lembretes diários para agendamentos do dia seguinte.
    """
    amanha = timezone.now().date() + timedelta(days=1)
    
    agendamentos = Agendamento.objects.filter(
        inicio__date=amanha,
        status__in=['pendente', 'confirmado']
    )
    
    notificacoes_criadas = 0
    
    for agendamento in agendamentos:
        # Verifica configuração do usuário
        config, created = ConfiguracaoNotificacao.objects.get_or_create(
            usuario=agendamento.cliente
        )
        
        if config.whatsapp_lembretes:
            low_priority_enviar_lembrete_agendamento.delay(agendamento.id)
            notificacoes_criadas += 1
    
    return f"Processados {notificacoes_criadas} lembretes para {amanha}"


@shared_task(queue='high')
def high_priority_enviar_whatsapp(telefone, mensagem):
    """
    Envia mensagem via WhatsApp (alta prioridade).
    """
    # Aqui seria implementada a integração com a API do WhatsApp
    # Por enquanto, apenas simula o envio
    
    print(f"Enviando WhatsApp para {telefone}: {mensagem}")
    
    # Simula delay de envio
    import time
    time.sleep(1)
    
    return f"WhatsApp enviado para {telefone}"


@shared_task(queue='low')
def low_priority_enviar_email(destinatario, assunto, corpo):
    """
    Envia e-mail (baixa prioridade).
    """
    # Aqui seria implementada a integração com serviço de e-mail
    # Por enquanto, apenas simula o envio
    
    print(f"Enviando e-mail para {destinatario}: {assunto}")
    
    # Simula delay de envio
    import time
    time.sleep(2)
    
    return f"E-mail enviado para {destinatario}"


@shared_task(queue='low')
def low_priority_limpar_notificacoes_antigas():
    """
    Remove notificações antigas (mais de 30 dias).
    """
    data_limite = timezone.now() - timedelta(days=30)
    
    notificacoes_removidas = Notificacao.objects.filter(
        data_envio__lt=data_limite,
        lida=True
    ).delete()[0]
    
    return f"Removidas {notificacoes_removidas} notificações antigas"
