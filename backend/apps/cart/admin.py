from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['sku', 'quantity', 'unit_price_cents', 'reserved_until']
    can_delete = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'identifier', 'total_items', 'subtotal_display', 'expires_at', 'status_display']
    list_filter = ['expires_at', 'created_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'subtotal_cents']
    inlines = [CartItemInline]

    fieldsets = (
        ('Identification', {
            'fields': ('id', 'session_id', 'user')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Summary', {
            'fields': ('subtotal_cents',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def identifier(self, obj):
        if obj.user:
            return f"User: {obj.user.username}"
        return f"Session: {obj.session_id[:20]}..."
    identifier.short_description = 'Cart Owner'

    def subtotal_display(self, obj):
        return f"R$ {obj.subtotal_cents / 100:.2f}"
    subtotal_display.short_description = 'Subtotal'

    def status_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    status_display.short_description = 'Status'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'sku', 'quantity', 'unit_price_display', 'reservation_status']
    list_filter = ['reserved_until', 'created_at']
    search_fields = ['cart__session_id', 'sku__sku_code']
    readonly_fields = ['id', 'cart', 'sku', 'created_at', 'updated_at']

    fieldsets = (
        ('Cart Item', {
            'fields': ('id', 'cart', 'sku', 'quantity')
        }),
        ('Pricing', {
            'fields': ('unit_price_cents',)
        }),
        ('Reservation', {
            'fields': ('reserved_until',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def unit_price_display(self, obj):
        return f"R$ {obj.unit_price_cents / 100:.2f}"
    unit_price_display.short_description = 'Unit Price'

    def reservation_status(self, obj):
        if obj.is_reservation_expired:
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Active</span>')
    reservation_status.short_description = 'Reservation'
