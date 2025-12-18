from django.db import models
from django.conf import settings
from apps.core.models import TimeStampedModel
from apps.products.models import SKU
import random
import string


class Order(TimeStampedModel):
    """
    Customer order with Brazilian address format.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Payment'
        CONFIRMED = 'CONFIRMED', 'Payment Confirmed'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    order_number = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        help_text="Human-readable order number"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Customer information
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=255)
    customer_cpf = models.CharField(
        max_length=14,
        help_text="Brazilian CPF (###.###.###-##)"
    )
    customer_phone = models.CharField(max_length=20)

    # Shipping address (Brazilian format)
    shipping_street = models.CharField(max_length=255)
    shipping_number = models.CharField(max_length=20)
    shipping_complement = models.CharField(max_length=255, blank=True)
    shipping_neighborhood = models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(
        max_length=2,
        help_text="Two-letter state code (e.g., SP, RJ)"
    )
    shipping_cep = models.CharField(
        max_length=9,
        help_text="Brazilian postal code (#####-###)"
    )

    # Pricing (in cents)
    subtotal_cents = models.IntegerField(help_text="Items subtotal in cents")
    shipping_cents = models.IntegerField(default=0, help_text="Shipping cost in cents")
    discount_cents = models.IntegerField(default=0, help_text="Total discount in cents")
    total_cents = models.IntegerField(help_text="Final total in cents")
    currency = models.CharField(max_length=3, default='BRL')

    # Additional info
    notes = models.TextField(blank=True, help_text="Customer notes")
    tracking_code = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['customer_email']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.customer_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_order_number():
        """
        Generate unique order number.
        Format: NCH-YYYYMMDD-XXXXX
        """
        from django.utils import timezone
        import random
        import string

        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=5))
        order_number = f"NCH-{date_part}-{random_part}"

        # Ensure uniqueness
        while Order.objects.filter(order_number=order_number).exists():
            random_part = ''.join(random.choices(string.digits, k=5))
            order_number = f"NCH-{date_part}-{random_part}"

        return order_number

    @property
    def total_items(self):
        """Total number of items in order."""
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal_brl(self):
        """Subtotal in BRL."""
        return self.subtotal_cents / 100

    @property
    def total_brl(self):
        """Total in BRL."""
        return self.total_cents / 100

    @property
    def full_address(self):
        """Formatted full address."""
        parts = [
            f"{self.shipping_street}, {self.shipping_number}",
        ]
        if self.shipping_complement:
            parts.append(self.shipping_complement)
        parts.extend([
            self.shipping_neighborhood,
            f"{self.shipping_city} - {self.shipping_state}",
            f"CEP: {self.shipping_cep}"
        ])
        return ', '.join(parts)


class OrderItem(TimeStampedModel):
    """
    Individual line item in an order.
    Captures product snapshot at time of purchase.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    sku = models.ForeignKey(
        SKU,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField()

    # Price snapshot
    unit_price_cents = models.IntegerField(
        help_text="Price per unit at time of purchase (in cents)"
    )

    line_total_cents = models.IntegerField(
        help_text="Total for this line item (in cents)"
    )

    # Product snapshot (for historical reference)
    product_snapshot = models.JSONField(
        help_text="Product details at time of purchase",
        default=dict
    )

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.sku.sku_code} in order {self.order.order_number}"

    def save(self, *args, **kwargs):
        # Calculate line total
        if not self.line_total_cents:
            self.line_total_cents = self.unit_price_cents * self.quantity

        # Capture product snapshot
        if not self.product_snapshot:
            self.product_snapshot = {
                'product_name': self.sku.product.name,
                'sku_code': self.sku.sku_code,
                'condition': self.sku.condition,
                'language': self.sku.language,
                'is_foil': self.sku.is_foil,
                'set_name': self.sku.product.set_name,
                'rarity': self.sku.product.rarity,
            }

        super().save(*args, **kwargs)

    @property
    def unit_price_brl(self):
        """Unit price in BRL."""
        return self.unit_price_cents / 100

    @property
    def line_total_brl(self):
        """Line total in BRL."""
        return self.line_total_cents / 100
