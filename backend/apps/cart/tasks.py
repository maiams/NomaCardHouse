from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_expired_carts():
    """
    Remove expired carts and release their inventory reservations.
    Runs periodically via Celery Beat.
    """
    from .models import Cart

    expired_carts = Cart.objects.filter(expires_at__lt=timezone.now())
    count = 0

    for cart in expired_carts:
        try:
            with transaction.atomic():
                # Clear with release_reservations=True (default) for expired carts
                cart.clear(release_reservations=True)
                cart.delete()
                count += 1
        except Exception as e:
            logger.error(f"Error cleaning up cart {cart.id}: {str(e)}")

    logger.info(f"Cleaned up {count} expired carts")
    return count


@shared_task
def cleanup_expired_reservations():
    """
    Release expired cart item reservations.
    Runs more frequently than cart cleanup.

    RESERVATION LIFECYCLE:
    - Explicitly release reservation first
    - Then delete item without re-releasing (prevents double-release)
    """
    from .models import CartItem

    expired_items = CartItem.objects.filter(
        reserved_until__lt=timezone.now()
    ).select_related('sku', 'cart')

    count = 0

    for item in expired_items:
        try:
            with transaction.atomic():
                # Release the reservation explicitly
                if hasattr(item.sku, 'inventory'):
                    item.sku.inventory.release(item.quantity)

                # Renew reservation if cart is still active
                if not item.cart.is_expired:
                    # Try to re-reserve
                    try:
                        item.sku.inventory.reserve(item.quantity)
                        item.renew_reservation()
                        logger.info(f"Renewed reservation for cart item {item.id}")
                    except Exception:
                        # Can't re-reserve (out of stock), remove item
                        # Delete without releasing (already released above)
                        item.delete()
                        logger.warning(f"Removed cart item {item.id} - stock unavailable")
                else:
                    # Cart expired, remove item
                    # Delete without releasing (already released above)
                    item.delete()

                count += 1
        except Exception as e:
            logger.error(f"Error processing expired reservation {item.id}: {str(e)}")

    logger.info(f"Processed {count} expired reservations")
    return count
