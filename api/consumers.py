import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Called when a WebSocket connection is opened."""
        token = self.get_token_from_query()

        if not token:
            await self.close()
            return

        user = await self.get_user_from_token(token)

        if not user:
            await self.close()
            return

        self.user = user
        self.group_name = f'notifications_{user.id}'

        # Join the user's personal notification group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected as {user.username}'
        }))

    async def disconnect(self, close_code):
        """Called when WebSocket connection is closed."""
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Called when a message is received from the client."""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'ping':
            await self.send(text_data=json.dumps({'type': 'pong'}))

    async def task_notification(self, event):
        """Called when a notification is pushed to this group."""
        await self.send(text_data=json.dumps({
            'type': 'task_notification',
            'message': event['message'],
            'task_id': event.get('task_id'),
            'notification_type': event.get('notification_type'),
        }))

    def get_token_from_query(self):
        """Extract JWT token from WebSocket URL query string."""
        query_string = self.scope.get('query_string', b'').decode()
        params = dict(
            param.split('=') for param in query_string.split('&')
            if '=' in param
        )
        return params.get('token')

    @database_sync_to_async
    def get_user_from_token(self, token):
        """Validate JWT token and return the user."""
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except (InvalidToken, TokenError, User.DoesNotExist):
            return None