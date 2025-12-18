from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, SKU
from .serializers import ProductListSerializer, ProductDetailSerializer, SKUSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for products.
    List and retrieve operations only (read-only for public API).
    """
    queryset = Product.objects.filter(is_active=True).prefetch_related('skus', 'skus__inventory')
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'set_name', 'rarity']
    search_fields = ['name', 'description', 'brand', 'set_name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer


class SKUViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for SKUs.
    """
    queryset = SKU.objects.filter(is_active=True).select_related('product', 'inventory')
    serializer_class = SKUSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'condition', 'language', 'is_foil']
    ordering_fields = ['price_cents']
    ordering = ['price_cents']
