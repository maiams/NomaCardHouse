"""
Stub payment provider for development and testing.
Returns fake payment data without actual payment processing.
"""

import hashlib
import hmac
import json
from datetime import timedelta
from typing import Dict, Any, Optional
from django.utils import timezone
from .base import (
    PaymentProvider,
    PaymentRequest,
    PaymentResponse,
    WebhookVerification
)


class StubPaymentProvider(PaymentProvider):
    """
    Fake payment provider for local development.
    Generates deterministic test data for all payment methods.
    """

    PROVIDER_NAME = 'stub'

    def create_payment(self, request: PaymentRequest) -> PaymentResponse:
        """
        Create a fake payment with realistic-looking data.
        """
        # Generate deterministic transaction ID
        transaction_id = self._generate_transaction_id(request.idempotency_key)

        # Base response
        response = PaymentResponse(
            success=True,
            provider_transaction_id=transaction_id,
            status='PENDING',
            expires_at=timezone.now() + timedelta(hours=24),
            fees_cents=self.calculate_fee(request.amount_cents, request.method),
            raw_payload={
                'stub': True,
                'request_data': {
                    'order_id': request.order_id,
                    'amount_cents': request.amount_cents,
                    'method': request.method,
                }
            }
        )

        # Method-specific data
        if request.method == 'PIX':
            response.pix_qr_code = self._generate_pix_qr_code(transaction_id)
            response.pix_copy_paste = self._generate_pix_copy_paste(transaction_id)
            response.expires_at = timezone.now() + timedelta(hours=2)

        elif request.method == 'BOLETO':
            response.boleto_url = f"https://stub-provider.local/boleto/{transaction_id}.pdf"
            response.boleto_barcode = self._generate_boleto_barcode(transaction_id)
            response.expires_at = timezone.now() + timedelta(days=3)

        elif request.method in ['CREDIT_CARD', 'DEBIT_CARD']:
            # In real implementation, this would return a redirect URL for 3DS
            response.redirect_url = f"https://stub-provider.local/card-auth/{transaction_id}"
            response.status = 'PROCESSING'

        return response

    def verify_webhook(
        self,
        headers: Dict[str, str],
        body: bytes
    ) -> WebhookVerification:
        """
        Verify webhook signature (stub implementation).
        In production, this would verify HMAC signature.
        """
        # For stub, always return valid
        try:
            payload = json.loads(body)
            return WebhookVerification(
                is_valid=True,
                provider_transaction_id=payload.get('transaction_id'),
                new_status=payload.get('status', 'COMPLETED'),
                paid_at=timezone.now() if payload.get('status') == 'COMPLETED' else None
            )
        except Exception as e:
            return WebhookVerification(
                is_valid=False,
                error_message=str(e)
            )

    def refund(
        self,
        transaction_id: str,
        amount_cents: Optional[int] = None
    ) -> bool:
        """
        Stub refund (always succeeds).
        """
        return True

    def get_status(self, transaction_id: str) -> str:
        """
        Stub status check (returns PENDING).
        """
        return 'PENDING'

    def calculate_fee(self, amount_cents: int, method: str) -> int:
        """
        Calculate stub fees (realistic percentages).
        """
        fee_rates = {
            'PIX': 0.0099,  # 0.99%
            'BOLETO': 0.0349,  # 3.49%
            'CREDIT_CARD': 0.0399,  # 3.99%
            'DEBIT_CARD': 0.0299,  # 2.99%
        }

        rate = fee_rates.get(method, 0.03)
        return int(amount_cents * rate)

    def _generate_transaction_id(self, idempotency_key: str) -> str:
        """
        Generate deterministic transaction ID from idempotency key.
        """
        hash_obj = hashlib.sha256(idempotency_key.encode())
        return f"STUB-{hash_obj.hexdigest()[:20].upper()}"

    def _generate_pix_qr_code(self, transaction_id: str) -> str:
        """
        Generate fake Pix QR code data.
        """
        # In reality, this would be EMV QR code format
        return f"00020126580014br.gov.bcb.pix0114{transaction_id}5204000053039865802BR5924Noma Card House6009SAO PAULO62070503***6304{transaction_id[:4]}"

    def _generate_pix_copy_paste(self, transaction_id: str) -> str:
        """
        Generate fake Pix copy-paste code.
        """
        return f"00020126580014br.gov.bcb.pix0114{transaction_id}5204000053039865802BR5924Noma Card House6009SAO PAULO62070503***6304{transaction_id[:4]}"

    def _generate_boleto_barcode(self, transaction_id: str) -> str:
        """
        Generate fake boleto barcode.
        Format: 47 digits (Brazilian boleto standard)
        """
        # Real boleto has specific format with bank code, currency, etc.
        hash_obj = hashlib.md5(transaction_id.encode())
        digits = ''.join(filter(str.isdigit, hash_obj.hexdigest()))
        return digits[:47].ljust(47, '0')


def get_payment_provider(provider_name: str = 'stub', config: Dict[str, Any] = None) -> PaymentProvider:
    """
    Factory function to get payment provider instance.

    Args:
        provider_name: Name of the provider (stub, mercadopago, asaas, etc.)
        config: Provider-specific configuration

    Returns:
        PaymentProvider instance
    """
    config = config or {}

    if provider_name == 'stub':
        return StubPaymentProvider(config)

    # Future providers can be added here:
    # elif provider_name == 'mercadopago':
    #     from .mercadopago import MercadoPagoProvider
    #     return MercadoPagoProvider(config)

    raise ValueError(f"Unknown payment provider: {provider_name}")
