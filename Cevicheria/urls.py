from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pedidos.views import CustomerViewSet, ProductViewSet, OrderViewSet,PublicOrderCreateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView  
from django.conf import settings
from django.conf.urls.static import static
from pedidos.views import webpay_init_transaction, webpay_commit_transaction
from pedidos.views import active_orders_count

from pedidos.views import pago_finalizado
# Rutas API REST
router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"products", ProductViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Documentación y esquema API
    #path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    #path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # Endpoints de la API
    path("api/", include(router.urls)),
    path("api/public/orders/", PublicOrderCreateView.as_view(), name="public-order-create"),

    # Páginas HTML  (Bootstrap)
    path("", TemplateView.as_view(template_name="menu.html"), name="home"),        
    path("nuevo/", TemplateView.as_view(template_name="order_new.html"), name="nuevo"),  
    path("index/", TemplateView.as_view(template_name="index.html"), name="index"),
    path("checkout/", TemplateView.as_view(template_name="checkout.html"), name="checkout"),

    path("api/webpay/init/<int:order_id>/", webpay_init_transaction, name="webpay-init"),
    path("api/webpay/return/", webpay_commit_transaction, name="webpay-return"),
    path("pago-finalizado/", pago_finalizado, name="pago-finalizado"),

    path("pago-finalizado/", TemplateView.as_view(template_name="pago_finalizado.html")),  
    path("pago-fallido/", TemplateView.as_view(template_name="pago_fallido.html")),
    path("api/public/orders/active-count/", active_orders_count, name="active-orders-count"),
        

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)