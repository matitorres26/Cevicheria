from rest_framework import serializers
from .models import Customer, Product, Order, OrderItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "name", "description", "price", "available", "image", "image_url")

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return "/static/images/default.jpg"


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product_name", "qty", "unit_price", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    # 👇 Nuevos campos que tu frontend necesita
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "customer",
            "name",
            "phone",
            "address",
            "email",
            "status",
            "total_price",
            "payment_method",
            "created_at",
            "updated_at",
            "items",
        )
        read_only_fields = ("created_at", "updated_at")

    # ==== DATOS DEL CLIENTE ====
    def get_name(self, obj):
        return obj.customer.name if obj.customer else ""

    def get_phone(self, obj):
        return obj.customer.phone if obj.customer else ""

    def get_address(self, obj):
        return obj.customer.address if obj.customer else ""

    def get_email(self, obj):
        return obj.customer.email if obj.customer else ""

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        order = Order.objects.create(**validated_data)
        total = 0
        for item in items_data:
            oi = OrderItem.objects.create(order=order, **item)
            total += oi.subtotal
        order.total_price = total
        order.save()
        return order

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PublicOrderItemSerializer(serializers.Serializer):
    product_name = serializers.CharField(max_length=120)
    qty = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)


class PublicOrderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=120)
    phone = serializers.CharField(max_length=32, allow_blank=True, required=False)
    address = serializers.CharField(max_length=255, allow_blank=True, required=False)
    email = serializers.EmailField(allow_blank=True, required=False)
    payment_method = serializers.ChoiceField(
        choices=[("CASH", "CASH"), ("WEBPAY", "WEBPAY"), ("MERCADOPAGO", "MERCADOPAGO")],
        default="CASH"
    )
    items = PublicOrderItemSerializer(many=True)

    def to_representation(self, instance):
        return OrderSerializer(instance).data

    def create(self, validated_data):
        items = validated_data.pop("items", [])
        customer = Customer.objects.create(
            name=validated_data.pop("name"),
            phone=validated_data.pop("phone", ""),
            address=validated_data.pop("address", ""),
            email=validated_data.pop("email", ""),
        )
        order = Order.objects.create(customer=customer, **validated_data)
        total = 0
        for it in items:
            oi = OrderItem.objects.create(order=order, **it)
            total += oi.subtotal
        order.total_price = total
        order.save()
        return order