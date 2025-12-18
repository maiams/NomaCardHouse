from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import SKUSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items.
    """
    sku = SKUSerializer(read_only=True)
    sku_id = serializers.UUIDField(write_only=True)
    line_total_brl = serializers.SerializerMethodField()
    unit_price_brl = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            'id',
            'sku',
            'sku_id',
            'quantity',
            'unit_price_cents',
            'unit_price_brl',
            'line_total_cents',
            'line_total_brl',
            'reserved_until',
            'is_reservation_expired',
        ]
        read_only_fields = [
            'unit_price_cents',
            'line_total_cents',
            'reserved_until',
        ]

    def get_line_total_brl(self, obj):
        return obj.line_total_cents / 100

    def get_unit_price_brl(self, obj):
        return obj.unit_price_cents / 100


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for shopping cart.
    """
    items = CartItemSerializer(many=True, read_only=True)
    subtotal_brl = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id',
            'session_id',
            'expires_at',
            'is_expired',
            'items',
            'total_items',
            'subtotal_cents',
            'subtotal_brl',
        ]
        read_only_fields = ['session_id', 'expires_at']

    def get_subtotal_brl(self, obj):
        return obj.subtotal_cents / 100


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer for adding items to cart.
    """
    sku_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.
    """
    quantity = serializers.IntegerField(min_value=0, max_value=99)
