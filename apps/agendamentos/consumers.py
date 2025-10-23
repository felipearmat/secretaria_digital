"""
WebSocket consumers for the appointments app.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.autenticacao.models import User


class AppointmentConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time appointment updates."""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'appointments_{self.room_name}'
        
        # Check if user is authenticated
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Adiciona ao grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recebe mensagem do WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'join_room':
                await self.send(text_data=json.dumps({
                    'type': 'room_joined',
                    'room': self.room_name
                }))
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensagem inválido'
            }))
    
    async def agendamento_update(self, event):
        """Envia atualização de agendamento para o cliente."""
        await self.send(text_data=json.dumps({
            'type': 'agendamento_update',
            'data': event['data']
        }))
    
    async def agendamento_created(self, event):
        """Envia notificação de novo agendamento."""
        await self.send(text_data=json.dumps({
            'type': 'agendamento_created',
            'data': event['data']
        }))
    
    async def agendamento_cancelled(self, event):
        """Envia notificação de agendamento cancelado."""
        await self.send(text_data=json.dumps({
            'type': 'agendamento_cancelled',
            'data': event['data']
        }))


class NotificacaoConsumer(AsyncWebsocketConsumer):
    """Consumer para notificações em tempo real."""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notificacoes_{self.user_id}'
        
        # Verifica se o usuário está autenticado
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Verifica se o usuário pode acessar as notificações
        user = await self.get_user()
        if not user or str(user.id) != self.user_id:
            await self.close()
            return
        
        # Adiciona ao grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recebe mensagem do WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'mark_as_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_as_read(notification_id)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato de mensagem inválido'
            }))
    
    @database_sync_to_async
    def get_user(self):
        """Obtém o usuário atual."""
        return self.scope['user']
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Marca notificação como lida."""
        from apps.notificacoes.models import Notificacao
        try:
            notification = Notificacao.objects.get(
                id=notification_id,
                usuario_id=self.user_id
            )
            notification.marcar_como_lida()
            return True
        except Notificacao.DoesNotExist:
            return False
    
    async def notificacao_nova(self, event):
        """Envia nova notificação para o cliente."""
        await self.send(text_data=json.dumps({
            'type': 'notificacao_nova',
            'data': event['data']
        }))
    
    async def notificacao_atualizada(self, event):
        """Envia notificação atualizada."""
        await self.send(text_data=json.dumps({
            'type': 'notificacao_atualizada',
            'data': event['data']
        }))
