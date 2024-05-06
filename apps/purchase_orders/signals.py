from django.db.models.signals import  post_save, pre_save
from .models import PurchaseOrder
from django.dispatch import receiver



@receiver(post_save, sender=PurchaseOrder)
def vendor_performance(sender, **kwargs):
    print(kwargs)
