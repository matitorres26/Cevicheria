from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Order

@receiver(post_save, sender=Order)
def notificar_nueva_orden(sender, instance, created, **kwargs):
    """
    NOTIFICAR SOLO CUANDO CORRESPONDA:

    - CASH → Notificar inmediatamente al crear.
    - WEBPAY → Notificar SOLO cuando se haya pagado (status = PAID).
    """

    # ⚠️ SI LA ORDEN ES NUEVA, PERO ES WEBPAY → NO NOTIFICAR
    if created and instance.payment_method == "WEBPAY":
        print(f"⏳ Pedido #{instance.id} Webpay creado, esperando pago. (Signal no envía)")
        return

    # ✔️ Si es CASH y recién creada → notificar
    if created and instance.payment_method == "CASH":
        enviar(instance)
        return

    # ✔️ Si es Webpay y acaba de cambiar a pagado → notificar
    if instance.payment_method == "WEBPAY" and instance.status == "PAID":
        enviar(instance)
        return


def enviar(order):
    layer = get_channel_layer()
    if layer is None:
        print("⚠️ No hay canal WebSocket activo")
        return

    try:
        async_to_sync(layer.group_send)(
            "orders",
            {
                "type": "new_order",
                "order_id": order.id,
            }
        )
        print(f"📣 Signal enviado → Pedido #{order.id}")
    except Exception as e:
        print(f"❌ Error enviando señal: {e}")
