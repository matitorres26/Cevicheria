from django.contrib import admin
from django.utils.html import format_html
from .models import Customer, Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_price", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("id", "customer__name", "customer__phone")
    inlines = [OrderItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "available", "image_tag")  # 🆕 muestra miniatura
    search_fields = ("name",)
    list_filter = ("available",)
    readonly_fields = ("image_tag",)  # 🆕 vista previa en detalle
    fields = ("name", "description", "price", "available", "image", "image_tag")  # orden del formulario

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" style="border-radius:10px;"/>', obj.image.url)
        return "— sin imagen —"
    image_tag.short_description = "Vista previa"  # título en la columna


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email")
    search_fields = ("name", "phone", "email")
