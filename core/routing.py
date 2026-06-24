"""
Routes WebSocket pour Django Channels.
Définit les URL WebSocket de l'application.
"""

from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    # Chat temps réel : ws://localhost:8001/ws/chat/
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()),
    
    # Notifications temps réel (pointages RFID, etc.) : ws://localhost:8001/ws/notifications/
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]
