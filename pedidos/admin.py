from django.contrib import admin
from .models import Customer, Product, Order, OrderItem

# Register your models here.
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "status", "total_price", "payment_method", "created_at")
    list_filter = ("status", "payment_method", "created_at")
    search_fields = ("id", "customer__name", "customer__phone")
    inlines = [OrderItemInline]

admin.site.register(Customer)
admin.site.register(Product)