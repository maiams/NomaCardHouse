from django.db import models
from apps.core.models import TimeStampedModel
from apps.orders.models import Order


class PaymentTransaction(TimeStampedModel):
    """
    Tracks payment transactions across different providers.
    """
    class Method(models.TextChoices):
        PIX = 'PIX', 'Pix'
        BOLETO = 'BOLETO', 'Boleto'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit Card'
        DEBIT_CARD = 'DEBIT_CARD', 'Debit Card'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REFUNDED = 'REFUNDED', 'Refunded'

    order = models.ForeignKey(
        Order,
        on_delete=models.PROTECT,
        related_name='payment_transactions'
    )

    # Idempotency
    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text="Unique key to prevent duplicate charges"
    )

    # Provider details
    provider = models.CharField(
        max_length=50,
        help_text="Payment provider name (e.g., mercadopago, asaas)"
    )

    provider_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        help_text="Transaction ID from payment provider"
    )

    # Payment details
    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    # Amounts (in cents)
    amount_cents = models.IntegerField(help_text="Payment amount in cents")
    fees_cents = models.IntegerField(
        null=True,
        blank=True,
        help_text="Provider fees in cents"
    )
    currency = models.CharField(max_length=3, default='BRL')

    # Payment method specific data
    pix_qr_code = models.TextField(
        blank=True,
        help_text="Pix QR code data"
    )

    pix_copy_paste = models.TextField(
        blank=True,
        help_text="Pix copy-paste code"
    )

    boleto_url = models.URLField(
        blank=True,
        help_text="Boleto PDF URL"
    )

    boleto_barcode = models.CharField(
        max_length=255,
        blank=True,
        help_text="Boleto barcode number"
    )

    # Timestamps
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Payment expiration (for Pix/Boleto)"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When payment was confirmed"
    )

    # Raw provider data
    raw_payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Raw response from payment provider"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order', 'status']),
            models.Index(fields=['provider', 'provider_transaction_id']),
            models.Index(fields=['method', 'status']),
        ]

    def __str__(self):
        return f"{self.method} payment for order {self.order.order_number} - {self.status}"

    @property
    def amount_brl(self):
        """Amount in BRL."""
        return self.amount_cents / 100

    @property
    def net_amount_cents(self):
        """Amount after fees."""
        if self.fees_cents:
            return self.amount_cents - self.fees_cents
        return self.amount_cents

    @property
    def is_expired(self):
        """Check if payment has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at

    @property
    def is_completed(self):
        """Check if payment is completed."""
        return self.status == self.Status.COMPLETED

    @property
    def is_pending(self):
        """Check if payment is pending."""
        return self.status in [self.Status.PENDING, self.Status.PROCESSING]
