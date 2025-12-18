from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
from apps.core.exceptions import InsufficientStockError, CartExpiredError, api_response
from apps.products.models import SKU
from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer
)
import uuid


class CartViewSet(viewsets.ViewSet):
    """
    API endpoints for shopping cart management.
    Uses session_id for cart identification.
    """

    def _get_or_create_cart(self, session_id):
        """Get or create cart for session."""
        cart, created = Cart.objects.get_or_create(
            session_id=session_id,
            defaults={'session_id': session_id}
        )

        if not created and cart.is_expired:
            # Clean up expired cart and create new one
            cart.clear()
            cart.delete()
            cart = Cart.objects.create(session_id=session_id)

        return cart

    def _get_session_id(self, request):
        """Extract session ID from request header or create new one."""
        session_id = request.headers.get('X-Session-ID')
        if not session_id:
            session_id = str(uuid.uuid4())
        return session_id

    def retrieve(self, request):
        """
        Get current cart.
        GET /api/v1/cart/
        """
        session_id = self._get_session_id(request)
        cart = self._get_or_create_cart(session_id)

        serializer = CartSerializer(cart)
        return api_response(
            data=serializer.data,
            message="Cart retrieved successfully"
        )

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add item to cart with inventory reservation.
        POST /api/v1/cart/add_item/
        Body: {"sku_id": "uuid", "quantity": 1}
        """
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = self._get_session_id(request)
        cart = self._get_or_create_cart(session_id)

        sku_id = serializer.validated_data['sku_id']
        quantity = serializer.validated_data['quantity']

        sku = get_object_or_404(SKU, id=sku_id, is_active=True)

        if not hasattr(sku, 'inventory'):
            return api_response(
                data=None,
                message="Product inventory not available",
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # Check if item already exists in cart
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    sku=sku,
                    defaults={'quantity': quantity}
                )

                if created:
                    # Reserve inventory for new item
                    sku.inventory.reserve(quantity)
                else:
                    # Update existing item quantity
                    cart_item.update_quantity(cart_item.quantity + quantity)

                # Extend cart expiration
                cart.extend_expiry()

        except InsufficientStockError as e:
            return api_response(
                data=None,
                message=str(e),
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Refresh cart data
        cart.refresh_from_db()
        serializer = CartSerializer(cart)

        return api_response(
            data=serializer.data,
            message="Item added to cart successfully",
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['patch'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        Update cart item quantity.
        PATCH /api/v1/cart/items/{item_id}/
        Body: {"quantity": 2}
        """
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session_id = self._get_session_id(request)
        cart = self._get_or_create_cart(session_id)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        new_quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                if new_quantity == 0:
                    # Remove item (user-initiated, must release reservation)
                    cart_item.release_and_delete()
                else:
                    # Update quantity
                    cart_item.update_quantity(new_quantity)

        except (InsufficientStockError, CartExpiredError) as e:
            return api_response(
                data=None,
                message=str(e),
                success=False,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Refresh cart data
        cart.refresh_from_db()
        serializer = CartSerializer(cart)

        return api_response(
            data=serializer.data,
            message="Cart updated successfully"
        )

    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def remove_item(self, request, item_id=None):
        """
        Remove item from cart.
        DELETE /api/v1/cart/items/{item_id}/
        """
        session_id = self._get_session_id(request)
        cart = self._get_or_create_cart(session_id)

        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

        with transaction.atomic():
            # User-initiated removal, must release reservation
            cart_item.release_and_delete()

        # Refresh cart data
        cart.refresh_from_db()
        serializer = CartSerializer(cart)

        return api_response(
            data=serializer.data,
            message="Item removed from cart"
        )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """
        Clear all items from cart.
        POST /api/v1/cart/clear/
        """
        session_id = self._get_session_id(request)
        cart = self._get_or_create_cart(session_id)

        with transaction.atomic():
            cart.clear()

        serializer = CartSerializer(cart)

        return api_response(
            data=serializer.data,
            message="Cart cleared successfully"
        )
