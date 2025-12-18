from django.db import models
from django.utils.text import slugify
from apps.core.models import TimeStampedModel


class Product(TimeStampedModel):
    """
    Represents a TCG product (card, sealed product, or accessory).
    """
    class Rarity(models.TextChoices):
        COMMON = 'COMMON', 'Common'
        UNCOMMON = 'UNCOMMON', 'Uncommon'
        RARE = 'RARE', 'Rare'
        MYTHIC = 'MYTHIC', 'Mythic Rare'
        SPECIAL = 'SPECIAL', 'Special'

    class Language(models.TextChoices):
        EN = 'EN', 'English'
        PT = 'PT', 'Portuguese'
        ES = 'ES', 'Spanish'
        JP = 'JP', 'Japanese'
        KO = 'KO', 'Korean'

    class Condition(models.TextChoices):
        MINT = 'MINT', 'Mint'
        NEAR_MINT = 'NEAR_MINT', 'Near Mint'
        LIGHTLY_PLAYED = 'LIGHTLY_PLAYED', 'Lightly Played'
        PLAYED = 'PLAYED', 'Played'
        DAMAGED = 'DAMAGED', 'Damaged'

    # Basic fields
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=300, unique=True, db_index=True)
    description = models.TextField(blank=True)
    brand = models.CharField(max_length=100, blank=True, help_text="e.g., Magic: The Gathering, Pokemon")

    # TCG-specific fields
    set_name = models.CharField(max_length=200, blank=True, help_text="Expansion or set name")
    tcg_number = models.CharField(max_length=50, blank=True, help_text="Collector number")
    rarity = models.CharField(max_length=20, choices=Rarity.choices, blank=True)

    # Product management
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'set_name']),
            models.Index(fields=['rarity']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class SKU(TimeStampedModel):
    """
    Represents a specific variant of a product with unique attributes.
    Each SKU has its own price and inventory.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='skus'
    )

    # SKU identifier
    sku_code = models.CharField(max_length=100, unique=True, db_index=True)

    # Variant attributes
    condition = models.CharField(
        max_length=20,
        choices=Product.Condition.choices,
        default=Product.Condition.NEAR_MINT
    )
    language = models.CharField(
        max_length=5,
        choices=Product.Language.choices,
        default=Product.Language.EN
    )
    is_foil = models.BooleanField(default=False)

    # Pricing (stored in cents to avoid decimal precision issues)
    price_cents = models.IntegerField(help_text="Price in BRL cents")
    sale_price_cents = models.IntegerField(
        null=True,
        blank=True,
        help_text="Sale price in BRL cents (if on sale)"
    )
    currency = models.CharField(max_length=3, default='BRL')

    # Availability
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['price_cents']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['condition', 'language']),
        ]
        verbose_name = 'SKU'
        verbose_name_plural = 'SKUs'

    def __str__(self):
        return f"{self.product.name} - {self.sku_code}"

    @property
    def effective_price_cents(self):
        """Returns sale price if available, otherwise regular price."""
        return self.sale_price_cents if self.sale_price_cents else self.price_cents

    @property
    def price_brl(self):
        """Returns price in BRL (converts cents to reais)."""
        return self.price_cents / 100

    @property
    def effective_price_brl(self):
        """Returns effective price in BRL."""
        return self.effective_price_cents / 100

    def generate_sku_code(self):
        """
        Generates a unique SKU code based on product and variant attributes.
        Format: {BRAND_PREFIX}-{SET_CODE}-{NUMBER}-{CONDITION}-{LANG}-{FOIL}
        """
        brand_prefix = self.product.brand[:3].upper() if self.product.brand else 'TCG'
        set_code = self.product.set_name[:3].upper() if self.product.set_name else 'XXX'
        number = self.product.tcg_number or '000'
        condition = self.condition[:2].upper()
        lang = self.language
        foil = 'F' if self.is_foil else 'N'

        base_code = f"{brand_prefix}-{set_code}-{number}-{condition}-{lang}-{foil}"

        # Ensure uniqueness
        code = base_code
        counter = 1
        while SKU.objects.filter(sku_code=code).exists():
            code = f"{base_code}-{counter}"
            counter += 1

        return code

    def save(self, *args, **kwargs):
        if not self.sku_code:
            self.sku_code = self.generate_sku_code()
        super().save(*args, **kwargs)
