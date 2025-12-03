import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import pedidos.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cevicheria.settings")

django_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            pedidos.routing.websocket_urlpatterns
        )
    ),
})