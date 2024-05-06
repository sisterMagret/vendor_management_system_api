from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.utils.abstracts import AbstractUUID
from apps.utils.country.countries import country_codes


class User(AbstractUser, AbstractUUID):
    """
    USER MODELS
    """

    mobile = models.CharField(unique=True, max_length=20)
    email = models.EmailField(max_length=255, null=True, blank=True, unique=True)
    country = models.CharField(
        max_length=30, choices=country_codes, null=True, blank=True
    )
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip_code = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    avatar = models.ImageField(upload_to="profile", null=True, blank=True)
    is_accept_terms_and_condition = models.BooleanField(
        default=False, blank=True
    )
    referral_code = models.CharField(max_length=255, null=True, blank=True, unique=True)
    updated_at = models.DateTimeField(auto_now=True, editable=False)
    date_joined = models.DateTimeField(
        auto_now_add=True, editable=False, null=True, blank=True
    )

    class Meta:
        db_table = "user"
        ordering = ("-date_joined",)

    def __str__(self):
        return f"{self.mobile} {self.get_full_name()} {self.id} {self.group()}"

    def group(self):
        if self.groups.all().count():
            return self.groups.all().first().name
        else:
            return "buyer"


class BuyerSettings(AbstractUUID):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer",
        null=True,
        blank=True,
    )
    business_name = models.CharField(max_length=255, null=True, blank=True)
    # interests

    def __str__(self):
        return f"{self.user.get_full_name()}"

    class Meta:
        ordering = ("-pk",)
        db_table = "buyer_settings"
        verbose_name = "Buyer Setting"
        verbose_name_plural = "Buyer Settings"


class VendorProfile(AbstractUUID):
    """Vendor Profile"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vendor",
        null=True,
        blank=True,
    )
    vendor_code = models.CharField(max_length=255, null=True, blank=True, unique=True)
    business_name = models.CharField(max_length=255, null=True, blank=True, unique=True)
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)