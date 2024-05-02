from datetime import date
import datetime
from django.test import TestCase

# Create your tests here.
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.purchase_orders.models import PurchaseOrder
from apps.utils.enums import POStatusEnum, QualityRatingEnum, UserGroup
from apps.vendors.models import VendorProfile


UserModel = get_user_model()


""" Modular Test """
# test user creation is working for all users
class VendorTestCase(TestCase):
    """TestCase for CustomBaseUser model"""
    current_date = datetime.datetime.now()
    def setUp(self) -> None:

        # create a new user
        self.user_payload = dict(
            first_name="John Doc",
            last_name="John Doe AB",
            email="john_doe@gmail.com",
            mobile="08139573300",
            password="$rootpa$$",
            username="john_doe",
            address="221B Baker Street",
            state="NY",
            country="USA",
            city="New York",
            postal_code="10001",
        )

        self.user = UserModel.objects.create(**self.user_payload)
        self.user.set_password(self.user_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
        self.user.groups.add(self.group)
        self.user.save()

        self.vendor_payload = dict(
            first_name="Sister",
            last_name="magret",
            email="sistermagret@gmail.com",
            mobile="08139572200",
            password="$rootpa$$",
            username="sistermagret",
            address="221B Baker Street",
            state="NY",
            country="USA",
            city="New York",
            postal_code="10001",
        )

        self.vendor_user = UserModel.objects.create(**self.vendor_payload)
        self.vendor_user.set_password(self.vendor_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
        self.user.groups.add(self.group)
        self.user.save()

        # create a new vendor
        self.vendor_data = dict(
            ref_code =  "123",
            user=self.vendor_user
        )

        self.vendor = VendorProfile.objects.create(**self.vendor_data)
        
        self.po_payload = dict(
            buyer = self.user,
            po_number = "123",
            vendor= self.vendor,
            order_date = self.current_date.strftime("%d:%m:%Y %H:%M:%S"),
            delivery_date= self.current_date.strftime("%d:%m:%Y %H:%M:%S"),
            items = ["playstation 5", "mc book"],
            quantity = 2,
            status= POStatusEnum.PENDING,
            total_amount= 100000,
            quality_rating = QualityRatingEnum.FIVE,
            issue_date= self.current_date.strftime("%d:%m:%Y %H:%M:%S"),
            acknowledgment_date=self.current_date.strftime("%d:%m:%Y %H:%M:%S"),
        )
        self.po = PurchaseOrder.objects.create(**self.po_payload)
    
    def test_po_creation(self):
        self.assertTrue(PurchaseOrder.objects.all().count() == 1)
        self.assertEqual(
            PurchaseOrder.objects.get(user__id=self.user.id), self.user.id
        )
        self.assertEqual(
            PurchaseOrder.objects.get(vendor__id=self.vendor.id), self.vendor.id
        )