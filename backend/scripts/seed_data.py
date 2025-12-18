"""
Seed script to populate database with sample TCG products.
Run with: python manage.py shell < scripts/seed_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from apps.products.models import Product, SKU
from apps.inventory.models import Inventory


def create_sample_products():
    """Create sample Magic: The Gathering products."""

    print("Creating sample products...")

    # Product 1: Black Lotus
    black_lotus = Product.objects.create(
        name="Black Lotus",
        description="Legendary power nine card. Add three mana of any one color.",
        brand="Magic: The Gathering",
        set_name="Alpha",
        tcg_number="232",
        rarity=Product.Rarity.SPECIAL,
    )

    SKU.objects.create(
        product=black_lotus,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=15000000,  # R$ 150,000.00
    )

    print(f"Created: {black_lotus.name}")

    # Product 2: Lightning Bolt
    lightning_bolt = Product.objects.create(
        name="Lightning Bolt",
        description="Deal 3 damage to any target.",
        brand="Magic: The Gathering",
        set_name="Core Set 2021",
        tcg_number="187",
        rarity=Product.Rarity.COMMON,
    )

    for condition in [Product.Condition.NEAR_MINT, Product.Condition.LIGHTLY_PLAYED]:
        for language in [Product.Language.EN, Product.Language.PT]:
            SKU.objects.create(
                product=lightning_bolt,
                condition=condition,
                language=language,
                is_foil=False,
                price_cents=500,  # R$ 5.00
            )

    SKU.objects.create(
        product=lightning_bolt,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=True,
        price_cents=2000,  # R$ 20.00
    )

    print(f"Created: {lightning_bolt.name}")

    # Product 3: Tarmogoyf
    tarmogoyf = Product.objects.create(
        name="Tarmogoyf",
        description="Legendary creature. Power and toughness based on card types in graveyards.",
        brand="Magic: The Gathering",
        set_name="Modern Horizons 2",
        tcg_number="182",
        rarity=Product.Rarity.RARE,
    )

    SKU.objects.create(
        product=tarmogoyf,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=8500,  # R$ 85.00
    )

    SKU.objects.create(
        product=tarmogoyf,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=True,
        price_cents=15000,  # R$ 150.00
    )

    print(f"Created: {tarmogoyf.name}")

    # Product 4: Force of Will
    force_of_will = Product.objects.create(
        name="Force of Will",
        description="Counter target spell. You may pay 1 life and exile a blue card instead.",
        brand="Magic: The Gathering",
        set_name="Alliances",
        tcg_number="42",
        rarity=Product.Rarity.RARE,
    )

    SKU.objects.create(
        product=force_of_will,
        condition=Product.Condition.LIGHTLY_PLAYED,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=12000,  # R$ 120.00
    )

    print(f"Created: {force_of_will.name}")

    # Product 5: Ragavan, Nimble Pilferer
    ragavan = Product.objects.create(
        name="Ragavan, Nimble Pilferer",
        description="Legendary Creature - Monkey Pirate. Dash, combat damage triggers.",
        brand="Magic: The Gathering",
        set_name="Modern Horizons 2",
        tcg_number="138",
        rarity=Product.Rarity.MYTHIC,
    )

    SKU.objects.create(
        product=ragavan,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=25000,  # R$ 250.00
    )

    SKU.objects.create(
        product=ragavan,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=True,
        price_cents=45000,  # R$ 450.00
    )

    print(f"Created: {ragavan.name}")

    # Product 6: Sol Ring
    sol_ring = Product.objects.create(
        name="Sol Ring",
        description="Artifact. Add two colorless mana.",
        brand="Magic: The Gathering",
        set_name="Commander Legends",
        tcg_number="865",
        rarity=Product.Rarity.UNCOMMON,
    )

    SKU.objects.create(
        product=sol_ring,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=300,  # R$ 3.00
    )

    print(f"Created: {sol_ring.name}")

    # Product 7: Counterspell
    counterspell = Product.objects.create(
        name="Counterspell",
        description="Counter target spell.",
        brand="Magic: The Gathering",
        set_name="Modern Horizons 2",
        tcg_number="267",
        rarity=Product.Rarity.COMMON,
    )

    for language in [Product.Language.EN, Product.Language.PT]:
        SKU.objects.create(
            product=counterspell,
            condition=Product.Condition.NEAR_MINT,
            language=language,
            is_foil=False,
            price_cents=400,  # R$ 4.00
        )

    print(f"Created: {counterspell.name}")

    # Product 8: Mox Opal
    mox_opal = Product.objects.create(
        name="Mox Opal",
        description="Legendary Artifact. Metalcraft - Add one mana of any color.",
        brand="Magic: The Gathering",
        set_name="Scars of Mirrodin",
        tcg_number="179",
        rarity=Product.Rarity.MYTHIC,
    )

    SKU.objects.create(
        product=mox_opal,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=18000,  # R$ 180.00
    )

    print(f"Created: {mox_opal.name}")

    # Product 9: Snapcaster Mage
    snapcaster = Product.objects.create(
        name="Snapcaster Mage",
        description="Creature - Human Wizard. Flash. Give instant/sorcery flashback.",
        brand="Magic: The Gathering",
        set_name="Innistrad",
        tcg_number="78",
        rarity=Product.Rarity.RARE,
    )

    SKU.objects.create(
        product=snapcaster,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=9500,  # R$ 95.00
    )

    print(f"Created: {snapcaster.name}")

    # Product 10: Fetchland - Scalding Tarn
    scalding_tarn = Product.objects.create(
        name="Scalding Tarn",
        description="Fetchland. Pay 1 life, sacrifice: Search for Island or Mountain.",
        brand="Magic: The Gathering",
        set_name="Modern Horizons 2",
        tcg_number="254",
        rarity=Product.Rarity.RARE,
    )

    SKU.objects.create(
        product=scalding_tarn,
        condition=Product.Condition.NEAR_MINT,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=3500,  # R$ 35.00
    )

    SKU.objects.create(
        product=scalding_tarn,
        condition=Product.Condition.LIGHTLY_PLAYED,
        language=Product.Language.EN,
        is_foil=False,
        price_cents=3200,  # R$ 32.00
    )

    print(f"Created: {scalding_tarn.name}")


def set_inventory_levels():
    """Set realistic inventory levels for all SKUs."""

    print("\nSetting inventory levels...")

    for inventory in Inventory.objects.all():
        sku_name = inventory.sku.product.name

        # High-value cards have lower stock
        if inventory.sku.price_cents >= 10000000:  # R$ 100,000+
            quantity = 1
        elif inventory.sku.price_cents >= 1000000:  # R$ 10,000+
            quantity = 2
        elif inventory.sku.price_cents >= 500000:  # R$ 5,000+
            quantity = 4
        elif inventory.sku.price_cents >= 100000:  # R$ 1,000+
            quantity = 8
        else:
            quantity = 20

        inventory.quantity_on_hand = quantity
        inventory.warehouse_location = f"SHELF-A-{inventory.sku.id.hex[:6].upper()}"
        inventory.save()

        print(f"Set inventory for {sku_name}: {quantity} units")


if __name__ == '__main__':
    print("=" * 50)
    print("NOMA CARD HOUSE - SEED DATA SCRIPT")
    print("=" * 50)

    # Clear existing data
    print("\nClearing existing products...")
    Product.objects.all().delete()

    # Create sample products
    create_sample_products()

    # Set inventory
    set_inventory_levels()

    print("\n" + "=" * 50)
    print("SEED DATA COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print(f"Total products created: {Product.objects.count()}")
    print(f"Total SKUs created: {SKU.objects.count()}")
    print(f"Total inventory records: {Inventory.objects.count()}")
