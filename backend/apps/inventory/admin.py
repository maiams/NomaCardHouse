from django.contrib import admin
from django.utils.html import format_html
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = [
        'sku',
        'quantity_on_hand',
        'quantity_reserved',
        'available_display',
        'stock_status',
        'warehouse_location'
    ]
    list_filter = ['last_restock_at']
    search_fields = ['sku__sku_code', 'sku__product__name', 'warehouse_location']
    readonly_fields = ['sku', 'created_at', 'updated_at', 'quantity_available']

    fieldsets = (
        ('SKU', {
            'fields': ('sku',)
        }),
        ('Stock Levels', {
            'fields': (
                'quantity_on_hand',
                'quantity_reserved',
                'quantity_available',
                'low_stock_threshold'
            )
        }),
        ('Warehouse', {
            'fields': ('warehouse_location', 'last_restock_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def available_display(self, obj):
        return obj.quantity_available
    available_display.short_description = 'Available'

    def stock_status(self, obj):
        if not obj.is_in_stock:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock</span>')
        else:
            return format_html('<span style="color: green;">In Stock</span>')
    stock_status.short_description = 'Status'

    def has_add_permission(self, request):
        # Inventory is auto-created via signals, disable manual add
        return False

    def has_delete_permission(self, request, obj=None):
        # Prevent accidental deletion
        return False
