import os, django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from pedidos.consumers import OrdersConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Cevicheria.settings")
django.setup()

django_asgi_app = get_asgi_application()

websocket_urlpatterns = [
    path("ws/orders/", OrdersConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_asgi_app,                               
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), 
})