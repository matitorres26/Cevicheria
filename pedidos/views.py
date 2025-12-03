from datetime import timedelta
from django.shortcuts import redirect, render
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.generics import CreateAPIView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import JsonResponse, HttpResponseRedirect
from django.conf import settings

from .models import Customer, Product, Order
from .serializers import (
    CustomerSerializer,
    ProductSerializer,
    OrderSerializer,
    PublicOrderSerializer,
)

# 🔹 Transbank SDK (v6.1.0)
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType


# ========================
#  HELPER WEBSOCKET
# ========================

def notify_new_order(order_id: int):
    """Envía la orden al grupo de WebSocket 'orders' (Tauri)."""
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        "orders",
        {"type": "new_order", "order_id": order_id},
    )


# ========================
#     API VIEWSETS
# ========================

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by("-id")
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by("name")
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.select_related("customer")
        .prefetch_related("items")
        .order_by("-id")
    )
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # 🚫 No notificamos aquí para no duplicar notificaciones
        order = serializer.save()
        print(
            f"🧾 Pedido #{order.id} creado desde API interna "
            f"(sin notificación automática)."
        )
        # Si algún día quieres que desde el panel se notifique:
        # notify_new_order(order.id)


# ========================
#     CREACIÓN PÚBLICA
# ========================

@method_decorator(csrf_exempt, name="dispatch")
class PublicOrderCreateView(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = PublicOrderSerializer

    def perform_create(self, serializer):
        order = serializer.save()
        payment_method = serializer.validated_data.get("payment_method") or "CASH"

        # 🔹 Estado inicial
        order.payment_method = payment_method
        order.payment_status = "PENDING"
        order.status = "NEW"
        order.save()

        print(f"🕓 Pedido #{order.id} creado ({payment_method})")

        # 💡 Lógica clave:
        #  - CASH (u otros que no sean WEBPAY) -> se notifica altiro
        #  - WEBPAY -> solo se notifica cuando el pago se autorice
        if payment_method == "WEBPAY":
            print(
                f"💳 Pedido #{order.id} con Webpay pendiente, "
                "NO se notifica todavía."
            )
        else:
            notify_new_order(order.id)
            print(f"💵 Pedido #{order.id} en {payment_method} notificado al local")


# ========================
#     WEBPAY INTEGRATION
# ========================

@csrf_exempt
def webpay_init_transaction(request, order_id):
    """Inicia una transacción Webpay Plus (SDK 6.1.0)"""
    try:
        order = Order.objects.get(id=order_id)

        # ✅ Crear opciones con las credenciales del ambiente de integración
        options = WebpayOptions(
            commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
            api_key=IntegrationApiKeys.WEBPAY,
            integration_type=IntegrationType.TEST,
        )

        tx = Transaction(options)

        buy_order = f"ORDER-{order.id}"
        session_id = f"SESSION-{order.id}"
        amount = float(order.total_price)
        return_url = settings.WEBPAY["RETURN_URL"]

        # Crear transacción
        response = tx.create(buy_order, session_id, amount, return_url)

        # Guardar información en la orden
        order.buy_order = buy_order
        order.session_id = session_id
        order.token_ws = response["token"]
        order.payment_method = "WEBPAY"
        order.save()

        return JsonResponse(
            {
                "url": response["url"],
                "token": response["token"],
            }
        )

    except Exception as e:
        print("❌ Error iniciando Webpay:", e)
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def webpay_commit_transaction(request):
    """Confirma una transacción Webpay Plus después del pago."""
    try:
        # 🔹 Obtener token desde POST o GET
        token = request.POST.get("token_ws") or request.GET.get("token_ws")
        if not token:
            print("⚠️ Token no recibido en POST ni GET")
            return JsonResponse({"error": "Token no recibido"}, status=400)

        # 🔹 Configuración de ambiente (integración)
        options = WebpayOptions(
            commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
            api_key=IntegrationApiKeys.WEBPAY,
            integration_type=IntegrationType.TEST,
        )

        tx = Transaction(options)
        response = tx.commit(token)
        print("💳 Respuesta de Webpay:", response)

        # 🔹 Buscar la orden asociada al token
        order = Order.objects.filter(token_ws=token).first()
        if not order:
            print("⚠️ No se encontró la orden con el token proporcionado.")
            return JsonResponse({"error": "Orden no encontrada"}, status=404)

        # =====================================================
        # 🔎 Validación real del resultado de la transacción
        # =====================================================
        status = response.get("status")
        response_code = response.get("response_code")
        vci = response.get("vci")

        # Caso exitoso
        if status == "AUTHORIZED" and response_code == 0 and vci == "TSY":
            order.status = "PAID"
            order.payment_status = "SUCCESS"
            order.save()

            # 🔔 Notificar al WebSocket SOLO ahora
            notify_new_order(order.id)

            print(f"✅ Pedido #{order.id} pagado correctamente y notificado.")
            return HttpResponseRedirect(f"/pago-finalizado/?order_id={order.id}")

        # Caso fallido o rechazado
        else:
            order.status = "FAILED"
            order.payment_status = "FAILED"
            order.save()

            print(
                f"❌ Pedido #{order.id} falló en el pago. "
                f"(status={status}, code={response_code}, vci={vci})"
            )
            return HttpResponseRedirect("/pago-fallido/")

    except Exception as e:
        print("❌ Error en commit Webpay:", e)
        return JsonResponse({"error": str(e)}, status=400)


def pago_finalizado(request):
    order_id = request.GET.get("order_id")

    if not order_id:
        return redirect("/")

    order = (
        Order.objects.select_related("customer")
        .prefetch_related("items")
        .filter(id=order_id)
        .first()
    )

    if not order:
        return redirect("/")

    # === Cálculo ETA ===
    from pedidos.consumers import calcular_tiempo_estimado

    eta_minutes = calcular_tiempo_estimado()
    ready_at = order.created_at + timedelta(minutes=eta_minutes)

    return render(
        request,
        "pago_finalizado.html",
        {
            "order": order,
            "items": order.items.all(),
            "eta_minutes": eta_minutes,
            "ready_at": ready_at,
        },
    )


def active_orders_count(request):
    count = Order.objects.filter(status__in=["NEW", "IN_PROGRESS"]).count()
    return JsonResponse({"count": count})
