from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, SKUViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')
router.register(r'skus', SKUViewSet, basename='sku')

urlpatterns = router.urls
