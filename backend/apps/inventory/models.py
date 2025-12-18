from django.db import models, transaction
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedModel
from apps.core.exceptions import InsufficientStockError
from apps.products.models import SKU


class Inventory(TimeStampedModel):
    """
    Tracks stock levels for each SKU with reservation support.
    """
    sku = models.OneToOneField(
        SKU,
        on_delete=models.CASCADE,
        related_name='inventory',
        unique=True
    )

    quantity_on_hand = models.IntegerField(
        default=0,
        help_text="Physical stock available"
    )

    quantity_reserved = models.IntegerField(
        default=0,
        help_text="Stock reserved in active carts"
    )

    warehouse_location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Physical location in warehouse"
    )

    last_restock_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time stock was replenished"
    )

    low_stock_threshold = models.IntegerField(
        default=5,
        help_text="Alert when stock falls below this number"
    )

    class Meta:
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return f"{self.sku.sku_code} - Available: {self.quantity_available}"

    @property
    def quantity_available(self):
        """Returns stock available for new reservations."""
        return max(0, self.quantity_on_hand - self.quantity_reserved)

    @property
    def is_low_stock(self):
        """Check if stock is below threshold."""
        return self.quantity_available <= self.low_stock_threshold

    @property
    def is_in_stock(self):
        """Check if any stock is available."""
        return self.quantity_available > 0

    def clean(self):
        """Validate that reserved quantity doesn't exceed on_hand."""
        if self.quantity_reserved > self.quantity_on_hand:
            raise ValidationError(
                "Reserved quantity cannot exceed quantity on hand"
            )

    @transaction.atomic
    def reserve(self, quantity):
        """
        Reserve stock for a cart item.
        Raises InsufficientStockError if not enough stock available.
        """
        # Lock the row for update to prevent race conditions
        inventory = Inventory.objects.select_for_update().get(id=self.id)

        if quantity > inventory.quantity_available:
            raise InsufficientStockError(
                f"Insufficient stock for {self.sku.sku_code}. "
                f"Available: {inventory.quantity_available}, Requested: {quantity}"
            )

        inventory.quantity_reserved += quantity
        inventory.save(update_fields=['quantity_reserved', 'updated_at'])

        return True

    @transaction.atomic
    def release(self, quantity):
        """
        Release reserved stock (e.g., when cart expires or item removed).

        IMPORTANT: Each reservation must be released exactly once.
        Do NOT call this after consume() - consume() already reduces reserved quantity.
        """
        inventory = Inventory.objects.select_for_update().get(id=self.id)

        # Defensive check: prevent negative reserved quantity
        if quantity > inventory.quantity_reserved:
            raise ValidationError(
                f"Cannot release {quantity} units - only {inventory.quantity_reserved} reserved. "
                f"Possible double-release detected for {self.sku.sku_code}"
            )

        inventory.quantity_reserved -= quantity
        inventory.save(update_fields=['quantity_reserved', 'updated_at'])

        return True

    @transaction.atomic
    def consume(self, quantity):
        """
        Consume reserved stock when order is confirmed.
        Reduces both on_hand and reserved quantities.
        """
        inventory = Inventory.objects.select_for_update().get(id=self.id)

        if quantity > inventory.quantity_reserved:
            raise ValidationError(
                f"Cannot consume {quantity} units - only {inventory.quantity_reserved} reserved"
            )

        if quantity > inventory.quantity_on_hand:
            raise ValidationError(
                f"Cannot consume {quantity} units - only {inventory.quantity_on_hand} on hand"
            )

        inventory.quantity_on_hand -= quantity
        inventory.quantity_reserved -= quantity
        inventory.save(update_fields=['quantity_on_hand', 'quantity_reserved', 'updated_at'])

        return True

    @transaction.atomic
    def restock(self, quantity):
        """
        Add new stock to inventory.
        """
        from django.utils import timezone

        inventory = Inventory.objects.select_for_update().get(id=self.id)
        inventory.quantity_on_hand += quantity
        inventory.last_restock_at = timezone.now()
        inventory.save(update_fields=['quantity_on_hand', 'last_restock_at', 'updated_at'])

        return True
