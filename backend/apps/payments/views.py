from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import PaymentTransaction
from apps.orders.models import Order
from .providers.stub import get_payment_provider
import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(APIView):
    """
    Webhook endpoint for payment provider callbacks.
    Validates webhook signature and updates payment status.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """
        Handle payment provider webhook.
        1. Verify webhook signature
        2. Parse payment update
        3. Update PaymentTransaction status
        4. Update Order status
        """
        # Get request body as bytes for signature verification
        body = request.body
        headers = {key: value for key, value in request.META.items() if key.startswith('HTTP_')}

        # Get payment provider (stub for now)
        provider = get_payment_provider('stub')

        # Verify webhook signature
        verification = provider.verify_webhook(headers, body)

        if not verification.is_valid:
            logger.warning(f"Invalid webhook signature: {verification.error_message}")
            return Response(
                {'success': False, 'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find payment transaction
        try:
            payment = PaymentTransaction.objects.select_for_update().get(
                provider_transaction_id=verification.provider_transaction_id
            )
        except PaymentTransaction.DoesNotExist:
            logger.error(f"Payment transaction not found: {verification.provider_transaction_id}")
            return Response(
                {'success': False, 'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Update payment status in transaction
        with transaction.atomic():
            # Update payment transaction
            old_status = payment.status
            payment.status = verification.new_status
            if verification.paid_at:
                payment.paid_at = verification.paid_at
            payment.save()

            # Update order status if payment completed
            if verification.new_status == 'COMPLETED' and old_status != 'COMPLETED':
                order = payment.order
                order.status = Order.Status.CONFIRMED
                order.save()

                logger.info(
                    f"Payment confirmed for order {order.order_number}, "
                    f"transaction {payment.provider_transaction_id}"
                )

        return Response(
            {
                'success': True,
                'message': 'Webhook processed successfully',
                'transaction_id': verification.provider_transaction_id,
                'status': verification.new_status
            },
            status=status.HTTP_200_OK
        )
