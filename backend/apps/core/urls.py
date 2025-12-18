from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('products/', include('apps.products.urls')),
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
]
