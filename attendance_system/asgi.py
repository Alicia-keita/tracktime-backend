"""
ASGI config for attendance_system project.
Gère à la fois les requêtes HTTP classiques (Django) et les connexions WebSocket (Django Channels).
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import core.routing

application = ProtocolTypeRouter({
    # Requêtes HTTP classiques → Django standard
    "http": get_asgi_application(),

    # WebSocket → Django Channels avec authentification JWT
    "websocket": AuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
