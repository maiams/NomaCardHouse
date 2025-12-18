from django.contrib import admin
from .models import Product, SKU


class SKUInline(admin.TabularInline):
    model = SKU
    extra = 1
    fields = ['sku_code', 'condition', 'language', 'is_foil', 'price_cents', 'sale_price_cents', 'is_active']
    readonly_fields = ['sku_code']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'set_name', 'rarity', 'is_active', 'created_at']
    list_filter = ['is_active', 'brand', 'rarity', 'created_at']
    search_fields = ['name', 'brand', 'set_name', 'tcg_number']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SKUInline]
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'brand', 'is_active')
        }),
        ('TCG Attributes', {
            'fields': ('set_name', 'tcg_number', 'rarity')
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ['sku_code', 'product', 'condition', 'language', 'is_foil', 'price_brl', 'is_active']
    list_filter = ['is_active', 'condition', 'language', 'is_foil']
    search_fields = ['sku_code', 'product__name']
    readonly_fields = ['id', 'sku_code', 'created_at', 'updated_at']

    fieldsets = (
        ('Product', {
            'fields': ('product',)
        }),
        ('SKU Details', {
            'fields': ('sku_code', 'condition', 'language', 'is_foil')
        }),
        ('Pricing', {
            'fields': ('price_cents', 'sale_price_cents', 'currency')
        }),
        ('Availability', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def price_brl(self, obj):
        return f"R$ {obj.price_brl:.2f}"
    price_brl.short_description = 'Price'
