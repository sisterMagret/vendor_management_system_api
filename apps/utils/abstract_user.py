from django.db import models


class VendorAbstract(models.Model):
    vendor = models.ForeignKey(
        "users.VendorProfile",
        related_name="%(class)s",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True

class BuyerAbstract(models.Model):
    buyer = models.ForeignKey(
        "users.BuyerSettings",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
