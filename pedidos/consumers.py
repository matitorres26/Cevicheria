import json
from datetime import timedelta
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Order, OrderItem


def calcular_tiempo_estimado():
    ahora = timezone.now()
    hora = ahora.hour

    base = 25

    if (12 <= hora <= 15) or (19 <= hora <= 21):
        base = 30

    activos = Order.objects.filter(status__in=["NEW", "IN_PROGRESS"]).count()

    extra = min(max(activos, 1), 25)

    total = min(max(base + extra, 20), 55)
    return total


class OrdersConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()
        print("🟢 Cliente conectado")

    async def disconnect(self, code):
        await self.channel_layer.group_discard("orders", self.channel_name)
        print("🔴 Cliente desconectado")

    async def new_order(self, event):
        order_id = event["order_id"]
        print(f"📨 Evento recibido → #{order_id}")

        data = await self.obtener(order_id)

        if data:
            await self.send(json.dumps({
                "type": "new_order",
                "order": data,
            }))
            print(f"📤 Enviado #{order_id} al cliente")

    @sync_to_async
    def obtener(self, order_id):
        try:
            order = Order.objects.select_related("customer").get(id=order_id)
            items = order.items.all()

            eta = calcular_tiempo_estimado()

            return {
                "id": order.id,
                "cliente": order.customer.name,
                "telefono": order.customer.phone,
                "direccion": order.customer.address,
                "email": order.customer.email,
                "pago": order.payment_method,
                "total": float(order.total_price),
                "status": order.status,
                "creado": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "eta_minutes": eta,
                "items": [
                    {
                        "producto": i.product_name,
                        "cantidad": i.qty,
                        "subtotal": float(i.subtotal),
                    }
                    for i in items
                ],
            }
        except:
            return None
