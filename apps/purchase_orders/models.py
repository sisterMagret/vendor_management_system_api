from django.db import models
from apps.utils.abstract_user import BuyerAbstract, VendorAbstract
from apps.utils.abstracts import AbstractUUID
from apps.utils.constant import DATETIME_FORMAT
from apps.utils.enums import POStatusEnum
from django.core.validators import DecimalValidator, MinValueValidator, MaxValueValidator
# Create your models here.


class Item(AbstractUUID):
    """Purchase Order Item"""
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(
        default=0.0,
         validators=[MinValueValidator(0.0), DecimalValidator(max_digits=16, decimal_places=1)]
        )

class PurchaseOrder(VendorAbstract, AbstractUUID):
    """Purchase Order"""
    buyer = models.ForeignKey(
        "users.User",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="user_purchase_order",
    )
    po_number = models.CharField(max_length=16, unique=True, editable=False)
    order_date = models.DateTimeField(auto_now=True, editable=False)
    delivery_date = models.DateTimeField()
    items = models.ManyToManyField(Item, related_name="items")
    quantity = models.PositiveIntegerField(default=1)
    status= models.CharField(
        max_length=20, choices=POStatusEnum.choices(), default=POStatusEnum.PENDING
    )
    quality_rating = models.FloatField(
        default=0.0,
         validators=[MinValueValidator(0.0), MaxValueValidator(5.0), DecimalValidator(max_digits=2, decimal_places=1)]
        )
    issue_date = models.DateTimeField(null=True, blank=True) #DateTimeField - Timestamp when the PO was issued to the vendor. 
    acknowledgment_date = models.DateTimeField(blank=True, null=True) #acknowledged the PO.
    updated_at = models.DateTimeField(auto_now=True, editable=False)
 

    class Meta:
        ordering = ("-order_date",)
        db_table = "purchase_order"
        verbose_name = "Purchase order"
        verbose_name_plural = "Purchase orders"

