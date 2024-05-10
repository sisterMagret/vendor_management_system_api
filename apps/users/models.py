from django.contrib.auth.models import AbstractUser
from django.db import models

from datetime import  timedelta
from django.db.models import Avg, F
from django.db.models.functions import TruncDay

from apps.utils.abstracts import AbstractUUID
from apps.utils.country.countries import country_codes
from apps.utils.enums import POStatusEnum

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
    """
    BUYER SETTINGS
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer",
        null=True,
        blank=True,
        editable=False
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
    """
    VENDOR PROFILE
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="vendor",
        null=True,
        blank=True,
        editable=False
    )
    vendor_code = models.CharField(max_length=255, null=True, blank=True, unique=True, editable=False)
    business_name = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def calculate_on_time_delivery_rate(self, completed_pos):
        """
        Calculate the on-time delivery rate for the vendor.
        """
        total_completed_pos = completed_pos.count()
        on_time_pos = completed_pos.filter(delivery_date__lte=F('order_date') + timedelta(days=10))
        on_time_delivery_rate = (on_time_pos.count() / total_completed_pos) * 100 if total_completed_pos > 0 else 0
        return on_time_delivery_rate

    def calculate_quality_rating_avg(self, completed_pos):
        """
        Calculate the average quality rating for the vendor.
        """
        quality_rating_avg = completed_pos.aggregate(avg_quality_rating=Avg('quality_rating'))['avg_quality_rating'] or 0
        return quality_rating_avg

    def calculate_avg_response_time(self, completed_pos):
        """
        Calculate the average response time for the vendor.
        """
        avg_response_time = completed_pos.annotate(
            response_time=TruncDay(F('acknowledgment_date')) - TruncDay(F('issue_date'))
        ).aggregate(avg_response_time=Avg('response_time'))['avg_response_time'] or 0
        return avg_response_time

    def calculate_fulfillment_rate(self, completed_pos, total_pos):
        """
        Calculate the fulfillment rate for the vendor.
        """
        fulfilled_pos = completed_pos.filter(status=POStatusEnum.COMPLETED)
        fulfillment_rate = (fulfilled_pos.count() / total_pos) * 100 if total_pos > 0 else 0
        return fulfillment_rate

    @property
    def calculate_performance_metrics(self):
        """
        Calculate the performance metrics for the vendor.
        """
        try:
            completed_pos = self.purchaseorder.filter(status=POStatusEnum.COMPLETED).select_related('vendor')

            on_time_delivery_rate = self.calculate_on_time_delivery_rate(completed_pos)
            quality_rating_avg = self.calculate_quality_rating_avg(completed_pos)
            avg_response_time = self.calculate_avg_response_time(completed_pos).total_seconds() / 86400
            total_pos = self.purchaseorder.all().count()
            fulfillment_rate = self.calculate_fulfillment_rate(completed_pos, total_pos)

            return{
                "on_time_delivery_rate": round(on_time_delivery_rate, 2),
                "quality_rating_avg": round(quality_rating_avg, 2),
                "average_response_time": avg_response_time,  # convert to days
                "fulfillment_rate": round(fulfillment_rate, 2)
            }
        except Exception as e:
            raise Exception(e)


class VendorHistoricalPerformance(AbstractUUID):
    """
    VENDOR HISTORICAL PERFORMANCE
    """

    vendor = models.ForeignKey(
        VendorProfile,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
        null=True,
        blank=True,
        editable=False
    )
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(default=0.0)
    quality_rating_avg = models.FloatField(default=0.0)
    average_response_time = models.FloatField(default=0.0)
    fulfillment_rate = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.date)
    class Meta:
        ordering = ["-date"]