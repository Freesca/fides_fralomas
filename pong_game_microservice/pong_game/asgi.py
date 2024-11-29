import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pong_game_ws.routing  # Importa il file di routing delle WebSocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_game.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pong_game_ws.routing.websocket_urlpatterns
        )
    ),
})