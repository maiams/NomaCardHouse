from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'method',
        'status_display',
        'amount_display',
        'provider',
        'created_at'
    ]
    list_filter = ['status', 'method', 'provider', 'created_at']
    search_fields = [
        'order__order_number',
        'provider_transaction_id',
        'idempotency_key'
    ]
    readonly_fields = [
        'id',
        'order',
        'idempotency_key',
        'provider_transaction_id',
        'created_at',
        'updated_at',
        'raw_payload'
    ]

    fieldsets = (
        ('Transaction', {
            'fields': (
                'id',
                'order',
                'idempotency_key',
                'status'
            )
        }),
        ('Provider', {
            'fields': (
                'provider',
                'provider_transaction_id',
            )
        }),
        ('Payment Details', {
            'fields': (
                'method',
                'amount_cents',
                'fees_cents',
                'currency'
            )
        }),
        ('Pix Details', {
            'fields': (
                'pix_qr_code',
                'pix_copy_paste'
            ),
            'classes': ('collapse',)
        }),
        ('Boleto Details', {
            'fields': (
                'boleto_url',
                'boleto_barcode'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'expires_at',
                'paid_at',
                'created_at',
                'updated_at'
            )
        }),
        ('Raw Data', {
            'fields': ('raw_payload',),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        color_map = {
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'COMPLETED': 'green',
            'FAILED': 'red',
            'CANCELLED': 'gray',
            'REFUNDED': 'purple',
        }
        color = color_map.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def amount_display(self, obj):
        return f"R$ {obj.amount_brl:.2f}"
    amount_display.short_description = 'Amount'
