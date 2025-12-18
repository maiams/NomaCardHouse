from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class PaymentRequest:
    """
    Unified payment creation request across all providers.
    """
    idempotency_key: str
    order_id: str
    order_number: str
    amount_cents: int
    method: str  # PIX, BOLETO, CREDIT_CARD, DEBIT_CARD
    currency: str = 'BRL'

    # Customer data
    customer_email: str = ''
    customer_name: str = ''
    customer_cpf: str = ''
    customer_phone: str = ''

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PaymentResponse:
    """
    Unified payment creation response.
    """
    success: bool
    provider_transaction_id: str
    status: str  # PENDING, PROCESSING, COMPLETED, FAILED

    # Payment method specific fields
    pix_qr_code: Optional[str] = None
    pix_copy_paste: Optional[str] = None
    boleto_url: Optional[str] = None
    boleto_barcode: Optional[str] = None
    redirect_url: Optional[str] = None  # For credit card 3DS

    # Expiration
    expires_at: Optional[datetime] = None

    # Provider fees
    fees_cents: Optional[int] = None

    # Raw provider response
    raw_payload: Optional[Dict[str, Any]] = None

    # Error details
    error_message: Optional[str] = None


@dataclass
class WebhookVerification:
    """
    Result of webhook signature verification.
    """
    is_valid: bool
    provider_transaction_id: Optional[str] = None
    new_status: Optional[str] = None
    paid_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers.
    All payment integrations must implement this interface.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration (API keys, secrets, etc.)
        """
        self.config = config

    @abstractmethod
    def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Create a payment transaction.

        Args:
            request: Payment request details

        Returns:
            PaymentResponse with transaction details and payment instructions

        Raises:
            PaymentProviderError: If payment creation fails
        """
        pass

    @abstractmethod
    def verify_webhook(
        self,
        headers: Dict[str, str],
        body: bytes
    ) -> WebhookVerification:
        """
        Verify webhook signature and extract payment update data.

        Args:
            headers: HTTP headers from webhook request
            body: Raw request body (for signature verification)

        Returns:
            WebhookVerification with validation result and payment data
        """
        pass

    @abstractmethod
    def refund(
        self,
        transaction_id: str,
        amount_cents: Optional[int] = None
    ) -> bool:
        """
        Process a refund (full or partial).

        Args:
            transaction_id: Provider's transaction ID
            amount_cents: Amount to refund (None for full refund)

        Returns:
            True if refund successful, False otherwise

        Raises:
            PaymentProviderError: If refund fails
        """
        pass

    @abstractmethod
    def get_status(self, transaction_id: str) -> str:
        """
        Poll payment status from provider.

        Args:
            transaction_id: Provider's transaction ID

        Returns:
            Current payment status (PENDING, COMPLETED, FAILED, etc.)

        Raises:
            PaymentProviderError: If status check fails
        """
        pass

    @abstractmethod
    def calculate_fee(self, amount_cents: int, method: str) -> int:
        """
        Calculate provider fee for a given amount and payment method.

        Args:
            amount_cents: Payment amount in cents
            method: Payment method (PIX, BOLETO, CREDIT_CARD, etc.)

        Returns:
            Fee amount in cents
        """
        pass
