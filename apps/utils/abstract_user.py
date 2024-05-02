from django.db import models


class FarmerAbstract(models.Model):
    farmer = models.ForeignKey(
        "users.FarmerSettings",
        related_name="%(class)s",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
