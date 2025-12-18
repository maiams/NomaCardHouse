"""
Tests for cart reservation lifecycle and double-release prevention.
"""

import pytest
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from apps.products.models import Product, SKU
from apps.inventory.models import Inventory
from apps.cart.models import Cart, CartItem
from apps.core.exceptions import InsufficientStockError


class InventoryReservationTestCase(TestCase):
    """Test inventory reservation logic."""

    def setUp(self):
        """Create test product and SKU with inventory."""
        self.product = Product.objects.create(
            name="Test Card",
            brand="Test TCG",
            set_name="Test Set",
            rarity=Product.Rarity.RARE,
        )

        self.sku = SKU.objects.create(
            product=self.product,
            condition=Product.Condition.NEAR_MINT,
            language=Product.Language.EN,
            is_foil=False,
            price_cents=1000,
        )

        # Inventory is auto-created via signal
        self.inventory = Inventory.objects.get(sku=self.sku)
        self.inventory.quantity_on_hand = 10
        self.inventory.save()

    def test_reserve_reduces_available(self):
        """Test that reserve() reduces available quantity."""
        initial_available = self.inventory.quantity_available
        self.inventory.reserve(3)
        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity_reserved, 3)
        self.assertEqual(self.inventory.quantity_available, initial_available - 3)

    def test_release_increases_available(self):
        """Test that release() increases available quantity."""
        self.inventory.reserve(5)
        self.inventory.refresh_from_db()

        self.inventory.release(3)
        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity_reserved, 2)
        self.assertEqual(self.inventory.quantity_available, 8)

    def test_release_prevents_negative_reserved(self):
        """Test that release() prevents negative reserved quantity."""
        self.inventory.reserve(3)
        self.inventory.refresh_from_db()

        # Try to release more than reserved
        with self.assertRaises(ValidationError) as context:
            self.inventory.release(5)

        self.assertIn("double-release", str(context.exception).lower())

    def test_consume_reduces_both_quantities(self):
        """Test that consume() reduces both on_hand and reserved."""
        self.inventory.reserve(5)
        self.inventory.refresh_from_db()

        initial_on_hand = self.inventory.quantity_on_hand
        initial_reserved = self.inventory.quantity_reserved

        self.inventory.consume(3)
        self.inventory.refresh_from_db()

        self.assertEqual(self.inventory.quantity_on_hand, initial_on_hand - 3)
        self.assertEqual(self.inventory.quantity_reserved, initial_reserved - 3)

    def test_consume_validates_reserved_quantity(self):
        """Test that consume() validates against reserved quantity."""
        self.inventory.reserve(3)
        self.inventory.refresh_from_db()

        # Try to consume more than reserved
        with self.assertRaises(ValidationError) as context:
            self.inventory.consume(5)

        self.assertIn("only 3 reserved", str(context.exception))


class CartItemReservationTestCase(TestCase):
    """Test cart item reservation lifecycle."""

    def setUp(self):
        """Create test cart and product."""
        self.product = Product.objects.create(
            name="Test Card",
            brand="Test TCG",
            set_name="Test Set",
            rarity=Product.Rarity.RARE,
        )

        self.sku = SKU.objects.create(
            product=self.product,
            condition=Product.Condition.NEAR_MINT,
            language=Product.Language.EN,
            is_foil=False,
            price_cents=1000,
        )

        self.inventory = Inventory.objects.get(sku=self.sku)
        self.inventory.quantity_on_hand = 20
        self.inventory.save()

        self.cart = Cart.objects.create(session_id="test-session-123")

    def test_add_to_cart_reserves_inventory(self):
        """Test that adding to cart reserves inventory."""
        initial_available = self.inventory.quantity_available

        # Reserve and create cart item
        self.inventory.reserve(2)
        cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=2,
        )

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 2)
        self.assertEqual(self.inventory.quantity_available, initial_available - 2)

    def test_release_and_delete_releases_once(self):
        """Test that release_and_delete() releases reservation exactly once."""
        # Create cart item with reservation
        self.inventory.reserve(3)
        cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=3,
        )

        self.inventory.refresh_from_db()
        reserved_before = self.inventory.quantity_reserved

        # Use release_and_delete
        cart_item.release_and_delete()

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, reserved_before - 3)

        # Verify cart item is deleted
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_delete_without_release(self):
        """Test that delete() does NOT release reservation."""
        # Create cart item with reservation
        self.inventory.reserve(3)
        cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=3,
        )

        self.inventory.refresh_from_db()
        reserved_before = self.inventory.quantity_reserved

        # Delete without release
        cart_item.delete()

        self.inventory.refresh_from_db()
        # Reservation should still be there
        self.assertEqual(self.inventory.quantity_reserved, reserved_before)

    def test_update_quantity_adjusts_reservation(self):
        """Test that update_quantity() properly adjusts reservation."""
        # Create cart item
        self.inventory.reserve(2)
        cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=2,
        )

        # Increase quantity
        cart_item.update_quantity(5)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 5)

        # Decrease quantity
        cart_item.update_quantity(3)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 3)


class CartClearTestCase(TestCase):
    """Test cart.clear() with and without releasing reservations."""

    def setUp(self):
        """Create test cart with items."""
        self.product = Product.objects.create(
            name="Test Card",
            brand="Test TCG",
            set_name="Test Set",
            rarity=Product.Rarity.RARE,
        )

        self.sku = SKU.objects.create(
            product=self.product,
            condition=Product.Condition.NEAR_MINT,
            language=Product.Language.EN,
            is_foil=False,
            price_cents=1000,
        )

        self.inventory = Inventory.objects.get(sku=self.sku)
        self.inventory.quantity_on_hand = 50
        self.inventory.save()

        self.cart = Cart.objects.create(session_id="test-session-123")

        # Add items to cart
        self.inventory.reserve(10)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=10,
        )

    def test_clear_with_release_default(self):
        """Test that clear() releases reservations by default."""
        self.inventory.refresh_from_db()
        reserved_before = self.inventory.quantity_reserved

        self.cart.clear()  # Default: release_reservations=True

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 0)
        self.assertEqual(self.cart.items.count(), 0)

    def test_clear_with_release_explicit_true(self):
        """Test clear(release_reservations=True) releases reservations."""
        self.inventory.refresh_from_db()

        self.cart.clear(release_reservations=True)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 0)
        self.assertEqual(self.cart.items.count(), 0)

    def test_clear_without_release(self):
        """Test clear(release_reservations=False) does NOT release."""
        self.inventory.refresh_from_db()
        reserved_before = self.inventory.quantity_reserved

        self.cart.clear(release_reservations=False)

        self.inventory.refresh_from_db()
        # Reservation should still exist
        self.assertEqual(self.inventory.quantity_reserved, reserved_before)
        # But items should be deleted
        self.assertEqual(self.cart.items.count(), 0)


class CheckoutFlowTestCase(TestCase):
    """Test checkout flow prevents double-release."""

    def setUp(self):
        """Create test cart ready for checkout."""
        self.product = Product.objects.create(
            name="Test Card",
            brand="Test TCG",
            set_name="Test Set",
            rarity=Product.Rarity.RARE,
        )

        self.sku = SKU.objects.create(
            product=self.product,
            condition=Product.Condition.NEAR_MINT,
            language=Product.Language.EN,
            is_foil=False,
            price_cents=1000,
        )

        self.inventory = Inventory.objects.get(sku=self.sku)
        self.inventory.quantity_on_hand = 100
        self.inventory.save()

        self.cart = Cart.objects.create(session_id="test-session-123")

        # Reserve and add to cart
        self.inventory.reserve(5)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            sku=self.sku,
            quantity=5,
        )

    def test_checkout_consume_then_clear_no_double_release(self):
        """
        Test that checkout flow (consume + clear) doesn't double-release.
        This simulates the actual checkout flow.
        """
        self.inventory.refresh_from_db()
        initial_on_hand = self.inventory.quantity_on_hand
        initial_reserved = self.inventory.quantity_reserved

        # Simulate checkout: consume inventory
        self.inventory.consume(5)
        self.inventory.refresh_from_db()

        # After consume: on_hand reduced, reserved reduced
        self.assertEqual(self.inventory.quantity_on_hand, initial_on_hand - 5)
        self.assertEqual(self.inventory.quantity_reserved, initial_reserved - 5)

        # Clear cart WITHOUT releasing (consume already did it)
        self.cart.clear(release_reservations=False)

        self.inventory.refresh_from_db()

        # Verify no double-release occurred
        self.assertEqual(self.inventory.quantity_on_hand, initial_on_hand - 5)
        self.assertEqual(self.inventory.quantity_reserved, 0)  # Should be 0 after consume
        self.assertEqual(self.cart.items.count(), 0)

    def test_checkout_wrong_clear_would_fail(self):
        """
        Test that using clear(release_reservations=True) after consume would fail.
        This demonstrates the bug we fixed.
        """
        self.inventory.refresh_from_db()
        initial_reserved = self.inventory.quantity_reserved

        # Consume inventory
        self.inventory.consume(5)
        self.inventory.refresh_from_db()

        # After consume, reserved should be 0
        self.assertEqual(self.inventory.quantity_reserved, 0)

        # Try to clear with release=True (the bug!)
        # This should raise ValidationError because there's nothing to release
        with self.assertRaises(ValidationError) as context:
            self.cart.clear(release_reservations=True)

        self.assertIn("double-release", str(context.exception).lower())


class ConcurrentReservationTestCase(TestCase):
    """Test concurrent cart operations."""

    def setUp(self):
        """Create test product with limited stock."""
        self.product = Product.objects.create(
            name="Test Card",
            brand="Test TCG",
            set_name="Test Set",
            rarity=Product.Rarity.RARE,
        )

        self.sku = SKU.objects.create(
            product=self.product,
            condition=Product.Condition.NEAR_MINT,
            language=Product.Language.EN,
            is_foil=False,
            price_cents=1000,
        )

        self.inventory = Inventory.objects.get(sku=self.sku)
        self.inventory.quantity_on_hand = 10  # Limited stock
        self.inventory.save()

    def test_insufficient_stock_prevents_oversell(self):
        """Test that reservations prevent overselling."""
        cart1 = Cart.objects.create(session_id="session-1")
        cart2 = Cart.objects.create(session_id="session-2")

        # Cart 1 reserves 6 items
        self.inventory.reserve(6)
        item1 = CartItem.objects.create(cart=cart1, sku=self.sku, quantity=6)

        # Cart 2 tries to reserve 6 items (should fail - only 4 available)
        with self.assertRaises(InsufficientStockError):
            self.inventory.reserve(6)

        # Cart 2 can reserve 4 items
        self.inventory.reserve(4)
        item2 = CartItem.objects.create(cart=cart2, sku=self.sku, quantity=4)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_reserved, 10)
        self.assertEqual(self.inventory.quantity_available, 0)

    def test_release_makes_stock_available_again(self):
        """Test that releasing reservation makes stock available."""
        cart = Cart.objects.create(session_id="test-session")

        # Reserve all stock
        self.inventory.reserve(10)
        item = CartItem.objects.create(cart=cart, sku=self.sku, quantity=10)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_available, 0)

        # Release some
        self.inventory.release(4)

        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity_available, 4)
        self.assertEqual(self.inventory.quantity_reserved, 6)
