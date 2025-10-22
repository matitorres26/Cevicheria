import json
from channels.generic.websocket import AsyncWebsocketConsumer

class OrdersConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("orders", self.channel_name)

    # Handler del evento enviado desde las views: {"type": "new.order", "order_id": ...}
    async def new_order(self, event):
        await self.send(json.dumps({
            "type": "new_order",
            "order_id": event["order_id"],
        }))