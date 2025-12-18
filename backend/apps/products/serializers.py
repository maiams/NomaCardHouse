from rest_framework import serializers
from .models import Product, SKU


class ProductSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight product info to embed in SKU responses.
    """

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'set_name',
            'rarity',
        ]


class SKUSerializer(serializers.ModelSerializer):
    """
    Serializer for SKU with inventory and pricing info.
    Includes lightweight product info for cart/order contexts.
    """
    price_brl = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    effective_price_brl = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    is_in_stock = serializers.SerializerMethodField()
    quantity_available = serializers.SerializerMethodField()
    product = ProductSummarySerializer(read_only=True)

    class Meta:
        model = SKU
        fields = [
            'id',
            'sku_code',
            'condition',
            'language',
            'is_foil',
            'price_cents',
            'sale_price_cents',
            'price_brl',
            'effective_price_brl',
            'currency',
            'is_active',
            'is_in_stock',
            'quantity_available',
            'product',
        ]

    def get_is_in_stock(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.is_in_stock
        return False

    def get_quantity_available(self, obj):
        if hasattr(obj, 'inventory'):
            return obj.inventory.quantity_available
        return 0


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for product list views.
    """
    min_price_brl = serializers.SerializerMethodField()
    is_in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'set_name',
            'rarity',
            'is_active',
            'min_price_brl',
            'is_in_stock',
        ]

    def get_min_price_brl(self, obj):
        """Get minimum price across all active SKUs."""
        skus = obj.skus.filter(is_active=True)
        if not skus.exists():
            return None

        min_price = min(sku.effective_price_cents for sku in skus)
        return min_price / 100

    def get_is_in_stock(self, obj):
        """Check if any SKU is in stock."""
        return any(
            hasattr(sku, 'inventory') and sku.inventory.is_in_stock
            for sku in obj.skus.filter(is_active=True)
        )


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full product details including all SKUs.
    """
    skus = SKUSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'brand',
            'set_name',
            'tcg_number',
            'rarity',
            'is_active',
            'skus',
            'created_at',
        ]
