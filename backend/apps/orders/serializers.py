from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items.
    """
    unit_price_brl = serializers.SerializerMethodField()
    line_total_brl = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'sku',
            'quantity',
            'unit_price_cents',
            'unit_price_brl',
            'line_total_cents',
            'line_total_brl',
            'product_snapshot',
        ]

    def get_unit_price_brl(self, obj):
        return obj.unit_price_brl

    def get_line_total_brl(self, obj):
        return obj.line_total_brl


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for orders.
    """
    items = OrderItemSerializer(many=True, read_only=True)
    subtotal_brl = serializers.SerializerMethodField()
    total_brl = serializers.SerializerMethodField()
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'customer_email',
            'customer_name',
            'customer_cpf',
            'customer_phone',
            'shipping_street',
            'shipping_number',
            'shipping_complement',
            'shipping_neighborhood',
            'shipping_city',
            'shipping_state',
            'shipping_cep',
            'full_address',
            'subtotal_cents',
            'subtotal_brl',
            'shipping_cents',
            'discount_cents',
            'total_cents',
            'total_brl',
            'currency',
            'items',
            'total_items',
            'notes',
            'tracking_code',
            'created_at',
        ]
        read_only_fields = [
            'order_number',
            'status',
            'subtotal_cents',
            'total_cents',
        ]

    def get_subtotal_brl(self, obj):
        return obj.subtotal_brl

    def get_total_brl(self, obj):
        return obj.total_brl


class CheckoutSerializer(serializers.Serializer):
    """
    Serializer for checkout request.
    """
    # Customer info
    customer_email = serializers.EmailField()
    customer_name = serializers.CharField(max_length=255)
    customer_cpf = serializers.CharField(max_length=14)
    customer_phone = serializers.CharField(max_length=20)

    # Shipping address
    shipping_street = serializers.CharField(max_length=255)
    shipping_number = serializers.CharField(max_length=20)
    shipping_complement = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_neighborhood = serializers.CharField(max_length=100)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=2)
    shipping_cep = serializers.CharField(max_length=9)

    # Payment
    payment_method = serializers.ChoiceField(
        choices=['PIX', 'BOLETO', 'CREDIT_CARD', 'DEBIT_CARD']
    )

    # Optional
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_shipping_state(self, value):
        """Validate Brazilian state code."""
        valid_states = [
            'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI',
            'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
        ]
        if value.upper() not in valid_states:
            raise serializers.ValidationError("Invalid Brazilian state code")
        return value.upper()

    def validate_customer_cpf(self, value):
        """Basic CPF format validation."""
        # Remove non-digit characters
        cpf = ''.join(filter(str.isdigit, value))

        if len(cpf) != 11:
            raise serializers.ValidationError("CPF must have 11 digits")

        return value
