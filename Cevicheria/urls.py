from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pedidos.views import (
    CustomerViewSet,
    ProductViewSet,
    OrderViewSet,
    PublicOrderCreateView,
    webpay_init_transaction,
    webpay_commit_transaction,
    active_orders_count,
    pago_finalizado,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Rutas API REST
router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"products", ProductViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API
    path("api/", include(router.urls)),
    path("api/public/orders/", PublicOrderCreateView.as_view(), name="public-order-create"),
    path("api/public/orders/active-count/", active_orders_count, name="active-orders-count"),

    # Páginas HTML
    path("", TemplateView.as_view(template_name="menu.html"), name="home"),
    path("nuevo/", TemplateView.as_view(template_name="order_new.html"), name="nuevo"),
    path("index/", TemplateView.as_view(template_name="index.html"), name="index"),
    path("checkout/", TemplateView.as_view(template_name="checkout.html"), name="checkout"),

    # WEBPAY
    path("api/webpay/init/<int:order_id>/", webpay_init_transaction, name="webpay_init"),
    path("webpay/commit/", webpay_commit_transaction, name="webpay_commit"),

    path("pago-finalizado/", pago_finalizado, name="pago_finalizado"),
    path("pago-fallido/", TemplateView.as_view(template_name="pago_fallido.html"), name="pago_fallido"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)