# pedidos/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Customer, Product, Order
from .serializers import (
    CustomerSerializer,
    ProductSerializer,
    OrderSerializer,
    PublicOrderSerializer,
)

# ---- API interna (admin/operación) ----
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-id")
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]  # endurecer luego si quieres

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("customer").prefetch_related("items").order_by("-id")
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        order = serializer.save()
        # Broadcast a todos los clientes WebSocket suscritos al grupo "orders"
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            "orders",
            {"type": "new.order", "order_id": order.id}
        )

# ---- API pública (checkout) ----
@method_decorator(csrf_exempt, name="dispatch")
class PublicOrderCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicOrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        # Broadcast cuando entra un pedido desde el checkout público
        layer = get_channel_layer()
        async_to_sync(layer.group_send)(
            "orders",
            {"type": "new.order", "order_id": order.id}
        )