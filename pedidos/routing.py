from django.urls import re_path

def get_orders_consumer():
    from .consumers import OrdersConsumer
    return OrdersConsumer

websocket_urlpatterns = [
    re_path(r"ws/orders/$", get_orders_consumer().as_asgi()),
]