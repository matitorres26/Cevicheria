import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class OrdersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()
        print("🟢 Cliente conectado al WebSocket")

    async def disconnect(self, code):
        await self.channel_layer.group_discard("orders", self.channel_name)
        print("🔴 Cliente desconectado del WebSocket")

    async def new_order(self, event):
        order_id = event["order_id"]
        print(f"📨 Recibido evento de nuevo pedido #{order_id}")

        order_data = await self.get_order_details(order_id)

        if not order_data:
            print(f"⚠️ Pedido #{order_id} no encontrado")
            return

        await self.send(json.dumps({
            "type": "new_order",
            "order": order_data,
        }))
        print(f"✅ Pedido #{order_id} enviado al cliente WebSocket")

    @sync_to_async
    def get_order_details(self, order_id):
        # 👇 Importar los modelos aquí, dentro del método
        from pedidos.models import Order, OrderItem

        try:
            order = Order.objects.select_related("customer").get(id=order_id)
            items = OrderItem.objects.filter(order=order)

            return {
                "id": order.id,
                "cliente": order.customer.name if order.customer else "Cliente desconocido",
                "telefono": order.customer.phone if order.customer else "",
                "direccion": order.customer.address if order.customer else "",
                "email": order.customer.email if order.customer else "",
                "pago": order.payment_method,
                "total": float(order.total_price or 0),
                "estado": order.status,
                "creado": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "items": [
                    {
                        "producto": i.product_name,
                        "cantidad": i.qty,
                        "subtotal": float(i.subtotal or 0),
                    }
                    for i in items
                ],
            }
        except Exception as e:
            print(f"❌ Error al obtener detalles del pedido #{order_id}: {e}")
            return None
