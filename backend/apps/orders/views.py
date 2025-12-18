from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.core.exceptions import api_response, CartExpiredError
from apps.cart.models import Cart
from apps.payments.models import PaymentTransaction
from apps.payments.providers.stub import get_payment_provider
from apps.payments.providers.base import PaymentRequest
from .models import Order, OrderItem
from .serializers import OrderSerializer, CheckoutSerializer
import uuid


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for orders.
    """
    queryset = Order.objects.all().prefetch_related('items')
    serializer_class = OrderSerializer
    lookup_field = 'order_number'

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        """
        Process checkout: create order and payment transaction.
        POST /api/v1/orders/checkout/
        """
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get session cart
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            return api_response(
                data=None,
                message="Session ID required",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        cart = get_object_or_404(Cart, session_id=session_id)

        if cart.is_expired:
            return api_response(
                data=None,
                message="Cart has expired",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if cart.total_items == 0:
            return api_response(
                data=None,
                message="Cart is empty",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer_email=serializer.validated_data['customer_email'],
                    customer_name=serializer.validated_data['customer_name'],
                    customer_cpf=serializer.validated_data['customer_cpf'],
                    customer_phone=serializer.validated_data['customer_phone'],
                    shipping_street=serializer.validated_data['shipping_street'],
                    shipping_number=serializer.validated_data['shipping_number'],
                    shipping_complement=serializer.validated_data.get('shipping_complement', ''),
                    shipping_neighborhood=serializer.validated_data['shipping_neighborhood'],
                    shipping_city=serializer.validated_data['shipping_city'],
                    shipping_state=serializer.validated_data['shipping_state'],
                    shipping_cep=serializer.validated_data['shipping_cep'],
                    notes=serializer.validated_data.get('notes', ''),
                    subtotal_cents=cart.subtotal_cents,
                    shipping_cents=0,  # Calculate shipping here if needed
                    discount_cents=0,  # Apply coupons here if needed
                    total_cents=cart.subtotal_cents,  # Adjust with shipping/discount
                )

                # Create order items and consume inventory
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        sku=cart_item.sku,
                        quantity=cart_item.quantity,
                        unit_price_cents=cart_item.unit_price_cents,
                    )

                    # Consume reserved inventory
                    cart_item.sku.inventory.consume(cart_item.quantity)

                # Create payment transaction
                payment_method = serializer.validated_data['payment_method']
                idempotency_key = f"{order.id}_{payment_method}_{uuid.uuid4().hex[:8]}"

                # Get payment provider (using stub for now)
                provider = get_payment_provider('stub')

                payment_request = PaymentRequest(
                    idempotency_key=idempotency_key,
                    order_id=str(order.id),
                    order_number=order.order_number,
                    amount_cents=order.total_cents,
                    method=payment_method,
                    customer_email=order.customer_email,
                    customer_name=order.customer_name,
                    customer_cpf=order.customer_cpf,
                    customer_phone=order.customer_phone,
                )

                payment_response = provider.create_payment(payment_request)

                if not payment_response.success:
                    raise Exception(payment_response.error_message or "Payment creation failed")

                # Save payment transaction
                payment_transaction = PaymentTransaction.objects.create(
                    order=order,
                    idempotency_key=idempotency_key,
                    provider='stub',
                    provider_transaction_id=payment_response.provider_transaction_id,
                    method=payment_method,
                    status=payment_response.status,
                    amount_cents=order.total_cents,
                    fees_cents=payment_response.fees_cents,
                    pix_qr_code=payment_response.pix_qr_code or '',
                    pix_copy_paste=payment_response.pix_copy_paste or '',
                    boleto_url=payment_response.boleto_url or '',
                    boleto_barcode=payment_response.boleto_barcode or '',
                    expires_at=payment_response.expires_at,
                    raw_payload=payment_response.raw_payload or {},
                )

                # Clear cart after successful checkout
                # Use release_reservations=False because consume() already handled it
                cart.clear(release_reservations=False)
                cart.delete()

        except Exception as e:
            return api_response(
                data=None,
                message=f"Checkout failed: {str(e)}",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Prepare response data
        order_serializer = OrderSerializer(order)
        response_data = {
            'order': order_serializer.data,
            'payment': {
                'transaction_id': str(payment_transaction.id),
                'method': payment_transaction.method,
                'status': payment_transaction.status,
                'amount_brl': payment_transaction.amount_brl,
                'pix_qr_code': payment_transaction.pix_qr_code,
                'pix_copy_paste': payment_transaction.pix_copy_paste,
                'boleto_url': payment_transaction.boleto_url,
                'boleto_barcode': payment_transaction.boleto_barcode,
                'expires_at': payment_transaction.expires_at,
            }
        }

        return api_response(
            data=response_data,
            message="Order created successfully",
            status_code=status.HTTP_201_CREATED
        )
