# Bug Fix: Inventory Reservation Double-Release Prevention

## Problem Summary

**Critical Bug:** Inventory reservations were being released twice during checkout and cart cleanup, causing `quantity_reserved` to become negative or incorrect, potentially leading to overselling.

## Root Cause

The `CartItem.delete()` method automatically released inventory reservations. This caused double-release in two scenarios:

1. **Checkout Flow:**
   - `inventory.consume()` reduces `quantity_reserved`
   - `cart.clear()` calls `item.delete()` which releases again
   - Result: `quantity_reserved` goes negative

2. **Expired Cart Cleanup:**
   - Task explicitly releases expired reservations
   - Then calls `item.delete()` which releases again
   - Result: `quantity_reserved` goes negative

## Solution: Explicit Reservation Lifecycle

Implemented **Approach B** (explicit methods) for clarity and safety:

### Core Changes

1. **Removed automatic release from `CartItem.delete()`**
   - `delete()` now ONLY deletes, never releases
   - Forces all callers to be explicit about intent

2. **Added `CartItem.release_and_delete()` method**
   - Explicitly releases reservation then deletes
   - Use for user-initiated removals

3. **Added `release_reservations` parameter to `Cart.clear()`**
   - `clear(release_reservations=True)` - for user actions, expired carts (default)
   - `clear(release_reservations=False)` - for post-checkout cleanup

4. **Added defensive checks to `Inventory.release()`**
   - Validates that quantity to release doesn't exceed reserved
   - Raises clear error if double-release attempted

## Reservation Lifecycle (Documented)

```
ADD TO CART:
  → inventory.reserve()
  → CartItem created

USER REMOVES ITEM:
  → item.release_and_delete()
  → Releases then deletes

CHECKOUT:
  → inventory.consume() (reduces on_hand AND reserved)
  → cart.clear(release_reservations=False)
  → Items deleted WITHOUT releasing

CART EXPIRES:
  → cart.clear(release_reservations=True)
  → Releases then deletes

RESERVATION EXPIRES:
  → inventory.release()
  → item.delete() (no release)
```

## Files Changed

### 1. `apps/inventory/models.py`
**Changes:**
- Added defensive check in `release()` to prevent negative reserved
- Added clear documentation about reservation lifecycle
- Raises `ValidationError` if double-release detected

### 2. `apps/cart/models.py`
**Changes:**
- Removed automatic release from `delete()`
- Added `release_and_delete()` method
- Added `release_reservations` parameter to `Cart.clear()`
- Added comprehensive documentation

### 3. `apps/cart/views.py`
**Changes:**
- Updated `update_item()` to use `release_and_delete()` when qty=0
- Updated `remove_item()` to use `release_and_delete()`
- No API behavior changed

### 4. `apps/orders/views.py`
**Changes:**
- Updated checkout to use `cart.clear(release_reservations=False)`
- Prevents double-release after `consume()`
- No API behavior changed

### 5. `apps/cart/tasks.py`
**Changes:**
- Explicitly documented cleanup logic
- `cleanup_expired_carts()` uses `clear(release_reservations=True)`
- `cleanup_expired_reservations()` explicitly releases before delete
- Added clear comments explaining lifecycle

### 6. `apps/cart/tests.py` (NEW)
**Added comprehensive tests:**
- Reservation reserve/release/consume operations
- Double-release prevention
- Cart clear with/without release
- Checkout flow correctness
- Concurrent reservation safety
- Oversell prevention

## Testing

Run tests to verify fix:

```bash
docker-compose exec backend pytest apps/cart/tests.py -v
```

### Test Coverage

✅ Reserve reduces available quantity
✅ Release increases available quantity
✅ Release prevents negative reserved (defensive check)
✅ Consume reduces both on_hand and reserved
✅ `release_and_delete()` releases exactly once
✅ `delete()` does NOT release
✅ `clear(release_reservations=True)` releases
✅ `clear(release_reservations=False)` does NOT release
✅ Checkout flow: consume + clear(False) = no double-release
✅ Wrong clear(True) after consume raises ValidationError
✅ Concurrent reservations prevent oversell

## Backward Compatibility

✅ **No API changes** - All endpoints unchanged
✅ **No response format changes** - Serializers unchanged
✅ **No database migrations** - Model fields unchanged
✅ **Default behavior preserved** - `clear()` defaults to `release_reservations=True`

## Safety Checklist

- [x] No double-release possible
- [x] All call sites updated
- [x] Defensive checks added to prevent negative reserved
- [x] Clear error messages on violations
- [x] Comprehensive tests added
- [x] Code documented with lifecycle comments
- [x] Transactional safety preserved
- [x] No API behavior changed
- [x] Code remains English-only
- [x] Minimal, focused changes only

## Verification Commands

```bash
# Run all cart tests
docker-compose exec backend pytest apps/cart/tests.py -v

# Run specific double-release test
docker-compose exec backend pytest apps/cart/tests.py::CheckoutFlowTestCase::test_checkout_consume_then_clear_no_double_release -v

# Run defensive check test
docker-compose exec backend pytest apps/cart/tests.py::InventoryReservationTestCase::test_release_prevents_negative_reserved -v

# Test full checkout flow via API
curl -X POST http://localhost:8000/api/v1/orders/checkout/ \
  -H "X-Session-ID: test-session" \
  -H "Content-Type: application/json" \
  -d '{...checkout data...}'
```

## Future Maintenance

**To prevent similar bugs:**

1. Always use `release_and_delete()` for user-initiated removals
2. Always use `clear(release_reservations=False)` after `consume()`
3. Trust defensive checks - if `ValidationError` raised, fix the caller
4. Follow documented reservation lifecycle
5. Add tests for new reservation scenarios

**Red flags:**
- Calling `release()` after `consume()`
- Calling `clear(release_reservations=True)` after `consume()`
- Modifying `delete()` to auto-release again
- Bypassing `release_and_delete()` in user actions

## Notes

This fix is **critical for production** - the double-release bug could cause inventory corruption and overselling. The explicit lifecycle approach prevents accidental misuse and makes the code self-documenting.
