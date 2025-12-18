from django.urls import path
from .views import CartViewSet

urlpatterns = [
    path('', CartViewSet.as_view({'get': 'retrieve'}), name='cart-detail'),
    path('add_item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('items/<uuid:item_id>/', CartViewSet.as_view({'patch': 'update_item', 'delete': 'remove_item'}), name='cart-item'),
    path('clear/', CartViewSet.as_view({'post': 'clear'}), name='cart-clear'),
]
