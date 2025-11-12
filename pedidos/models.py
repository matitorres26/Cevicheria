from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    
    image = models.ImageField(upload_to="products/", blank=True, null=True) 

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ("NEW", "Nuevo"),
        ("IN_PROGRESS", "En preparación"),
        ("READY", "Listo"),
        ("DELIVERED", "Entregado"),
        ("PAID", "Pagado"),  
        ("FAILED", "Fallido"), 
    ]

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="NEW")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, default="CASH")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    token_ws = models.CharField(max_length=255, blank=True, null=True)
    buy_order = models.CharField(max_length=100, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=20, default="PENDING")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_name = models.CharField(max_length=120)
    qty = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)


class DailyReport(models.Model):
    date = models.DateField(unique=True)
    total_orders = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.date}"
    
    