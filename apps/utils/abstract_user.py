from django.db import models


class VendorAbstract(models.Model):
    vendor = models.ForeignKey(
        "authentication.VendorProfile",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
