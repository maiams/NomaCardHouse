from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['sku', 'quantity', 'unit_price_display', 'line_total_display', 'product_snapshot']
    can_delete = False

    def unit_price_display(self, obj):
        return f"R$ {obj.unit_price_brl:.2f}"
    unit_price_display.short_description = 'Unit Price'

    def line_total_display(self, obj):
        return f"R$ {obj.line_total_brl:.2f}"
    line_total_display.short_description = 'Line Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'customer_name',
        'status_display',
        'total_display',
        'created_at'
    ]
    list_filter = ['status', 'created_at', 'shipping_state']
    search_fields = [
        'order_number',
        'customer_name',
        'customer_email',
        'customer_cpf',
        'tracking_code'
    ]
    readonly_fields = [
        'id',
        'order_number',
        'created_at',
        'updated_at',
        'full_address'
    ]
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'order_number', 'user', 'status')
        }),
        ('Customer Details', {
            'fields': (
                'customer_name',
                'customer_email',
                'customer_cpf',
                'customer_phone'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_street',
                'shipping_number',
                'shipping_complement',
                'shipping_neighborhood',
                'shipping_city',
                'shipping_state',
                'shipping_cep',
                'full_address',
                'tracking_code'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal_cents',
                'shipping_cents',
                'discount_cents',
                'total_cents',
                'currency'
            )
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        color_map = {
            'PENDING': 'orange',
            'CONFIRMED': 'blue',
            'PROCESSING': 'purple',
            'SHIPPED': 'teal',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
            'REFUNDED': 'gray',
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def total_display(self, obj):
        return f"R$ {obj.total_brl:.2f}"
    total_display.short_description = 'Total'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'sku',
        'quantity',
        'unit_price_display',
        'line_total_display'
    ]
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'sku__sku_code']
    readonly_fields = ['id', 'created_at', 'updated_at', 'product_snapshot']

    def unit_price_display(self, obj):
        return f"R$ {obj.unit_price_brl:.2f}"
    unit_price_display.short_description = 'Unit Price'

    def line_total_display(self, obj):
        return f"R$ {obj.line_total_brl:.2f}"
    line_total_display.short_description = 'Line Total'
