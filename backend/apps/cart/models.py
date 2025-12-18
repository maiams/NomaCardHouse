from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from apps.core.models import TimeStampedModel
from apps.core.exceptions import InsufficientStockError, CartExpiredError
from apps.products.models import SKU


class Cart(TimeStampedModel):
    """
    Shopping cart with automatic expiration.
    Can be anonymous (session-based) or authenticated (user-based).
    """
    session_id = models.CharField(
        max_length=255,
        db_index=True,
        help_text="Session identifier for anonymous carts"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts',
        help_text="Authenticated user (optional)"
    )

    expires_at = models.DateTimeField(
        db_index=True,
        help_text="Cart expiration timestamp"
    )

    class Meta:
        indexes = [
            models.Index(fields=['session_id', 'expires_at']),
        ]

    def __str__(self):
        identifier = self.user.username if self.user else self.session_id
        return f"Cart for {identifier}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                days=settings.CART_EXPIRY_DAYS
            )
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if cart has expired."""
        return timezone.now() > self.expires_at

    @property
    def subtotal_cents(self):
        """Calculate cart subtotal in cents."""
        return sum(item.line_total_cents for item in self.items.all())

    @property
    def total_items(self):
        """Total number of items in cart."""
        return sum(item.quantity for item in self.items.all())

    def extend_expiry(self):
        """Extend cart expiration when user interacts with it."""
        self.expires_at = timezone.now() + timedelta(days=settings.CART_EXPIRY_DAYS)
        self.save(update_fields=['expires_at', 'updated_at'])

    @transaction.atomic
    def clear(self, release_reservations=True):
        """
        Remove all items from cart.

        Args:
            release_reservations: If True, release inventory reservations.
                                 Set to False after checkout (consume already released).

        USAGE:
        - User clears cart: cart.clear(release_reservations=True) [default]
        - After checkout: cart.clear(release_reservations=False)
        - Expired cart cleanup: cart.clear(release_reservations=True) [default]
        """
        for item in self.items.all():
            if release_reservations:
                item.release_and_delete()
            else:
                # Reservation already handled (e.g., consumed during checkout)
                item.delete()


class CartItem(TimeStampedModel):
    """
    Individual item in a cart with inventory reservation.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    sku = models.ForeignKey(
        SKU,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    quantity = models.PositiveIntegerField(default=1)

    reserved_until = models.DateTimeField(
        db_index=True,
        help_text="Inventory reservation expiration"
    )

    unit_price_cents = models.IntegerField(
        help_text="Price snapshot when added to cart (in cents)"
    )

    class Meta:
        unique_together = [['cart', 'sku']]
        indexes = [
            models.Index(fields=['reserved_until']),
        ]

    def __str__(self):
        return f"{self.quantity}x {self.sku.sku_code} in cart {self.cart.id}"

    def save(self, *args, **kwargs):
        # Snapshot price when item is created
        if not self.unit_price_cents:
            self.unit_price_cents = self.sku.effective_price_cents

        # Set reservation expiration
        if not self.reserved_until:
            self.reserved_until = timezone.now() + timedelta(
                minutes=settings.CART_RESERVATION_TIMEOUT_MINUTES
            )

        super().save(*args, **kwargs)

    @property
    def line_total_cents(self):
        """Calculate line total in cents."""
        return self.unit_price_cents * self.quantity

    @property
    def is_reservation_expired(self):
        """Check if inventory reservation has expired."""
        return timezone.now() > self.reserved_until

    def renew_reservation(self):
        """Extend reservation timeout."""
        self.reserved_until = timezone.now() + timedelta(
            minutes=settings.CART_RESERVATION_TIMEOUT_MINUTES
        )
        self.save(update_fields=['reserved_until', 'updated_at'])

    @transaction.atomic
    def update_quantity(self, new_quantity):
        """
        Update item quantity and adjust inventory reservation.
        """
        if self.cart.is_expired:
            raise CartExpiredError("Cannot modify expired cart")

        if self.is_reservation_expired:
            # Release old reservation
            self.sku.inventory.release(self.quantity)
            # Re-reserve with new quantity
            self.sku.inventory.reserve(new_quantity)
            self.renew_reservation()
        else:
            # Adjust existing reservation
            quantity_diff = new_quantity - self.quantity

            if quantity_diff > 0:
                # Reserve additional stock
                self.sku.inventory.reserve(quantity_diff)
            elif quantity_diff < 0:
                # Release excess stock
                self.sku.inventory.release(abs(quantity_diff))

        self.quantity = new_quantity
        self.save(update_fields=['quantity', 'updated_at'])

    def release_and_delete(self):
        """
        Release inventory reservation and delete cart item.
        Use this when user explicitly removes item from cart.

        RESERVATION LIFECYCLE:
        - User adds to cart: inventory.reserve() is called
        - User removes from cart: call this method (release + delete)
        - Checkout consumes: inventory.consume() then delete() without release
        - Cart expires: release reservation then delete() without release
        """
        if hasattr(self.sku, 'inventory'):
            self.sku.inventory.release(self.quantity)
        self.delete()

    def delete(self, *args, **kwargs):
        """
        Delete cart item WITHOUT releasing reservation.

        WARNING: This does NOT release inventory automatically.
        Caller must explicitly release reservation if needed via:
        - release_and_delete() for user removals
        - inventory.release() before delete() for expirations
        - inventory.consume() before delete() for checkout

        This prevents double-release bugs where reservation is
        released once explicitly and again implicitly.
        """
        super().delete(*args, **kwargs)
