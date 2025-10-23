"""
Configuração de rotas WebSocket para o app de agendamentos.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/agendamentos/(?P<room_name>\w+)/$', consumers.AgendamentoConsumer.as_asgi()),
    re_path(r'ws/notificacoes/(?P<user_id>\w+)/$', consumers.NotificacaoConsumer.as_asgi()),
]
