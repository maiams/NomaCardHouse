from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.products.models import SKU
from .models import Inventory


@receiver(post_save, sender=SKU)
def create_inventory_for_sku(sender, instance, created, **kwargs):
    """
    Auto-create Inventory record when a new SKU is created.
    """
    if created:
        Inventory.objects.create(sku=instance)
