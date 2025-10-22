"""
URL configuration for cevicheria project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from pedidos.views import CustomerViewSet, ProductViewSet, OrderViewSet,PublicOrderCreateView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.generic import TemplateView  

# Rutas API REST
router = DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"products", ProductViewSet)
router.register(r"orders", OrderViewSet)

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Documentación y esquema API
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema")),

    # Endpoints de la API
    path("api/", include(router.urls)),
    path("api/public/orders/", PublicOrderCreateView.as_view(), name="public-order-create"),

    # Páginas HTML  (Bootstrap)
    path("", TemplateView.as_view(template_name="index.html"), name="home"),        
    path("nuevo/", TemplateView.as_view(template_name="order_new.html"), name="nuevo"),  
    path("menu/", TemplateView.as_view(template_name="menu.html"), name="menu"),
    path("checkout/", TemplateView.as_view(template_name="checkout.html"), name="checkout"),
]
