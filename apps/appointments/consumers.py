"""
WebSocket consumers for the appointments app.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from apps.authentication.models import User


class AppointmentConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time appointment updates."""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'appointments_{self.room_name}'
        
        # Check if user is authenticated
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Add to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove from group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receives WebSocket message."""
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
                'message': 'Invalid message format'
            }))
    
    async def appointment_update(self, event):
        """Sends appointment update to client."""
        await self.send(text_data=json.dumps({
            'type': 'appointment_update',
            'data': event['data']
        }))
    
    async def appointment_created(self, event):
        """Sends new appointment notification."""
        await self.send(text_data=json.dumps({
            'type': 'appointment_created',
            'data': event['data']
        }))
    
    async def appointment_cancelled(self, event):
        """Sends cancelled appointment notification."""
        await self.send(text_data=json.dumps({
            'type': 'appointment_cancelled',
            'data': event['data']
        }))


class NotificacaoConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time notifications."""
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notifications_{self.user_id}'
        
        # Check if user is authenticated
        if self.scope['user'] == AnonymousUser():
            await self.close()
            return
        
        # Check if user can access notifications
        user = await self.get_user()
        if not user or str(user.id) != self.user_id:
            await self.close()
            return
        
        # Add to group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Remove from group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Receives WebSocket message."""
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
                'message': 'Invalid message format'
            }))
    
    @database_sync_to_async
    def get_user(self):
        """Gets the current user."""
        return self.scope['user']
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Marks notification as read."""
        from apps.notifications.models import Notification
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user_id=self.user_id
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    async def new_notification(self, event):
        """Sends new notification to client."""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'data': event['data']
        }))
    
    async def notification_updated(self, event):
        """Sends updated notification."""
        await self.send(text_data=json.dumps({
            'type': 'notification_updated',
            'data': event['data']
        }))
