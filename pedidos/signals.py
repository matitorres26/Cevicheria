from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Order

@receiver(post_save, sender=Order)
def notificar_nueva_orden(sender, instance, created, **kwargs):
    if not created:
        return

    layer = get_channel_layer()
    if layer is None:
        print("⚠️ No hay canal WebSocket activo")
        return

    try:
        async_to_sync(layer.group_send)(
            "orders",
            {
                "type": "new_order",
                "order_id": instance.id,
            }
        )
        print(f"📣 Signal enviado → Pedido #{instance.id}")
    except Exception as e:
        print(f"❌ Error enviando señal: {e}")
