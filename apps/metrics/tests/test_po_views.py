from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test import TestCase
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient

from apps.purchase_orders.models import PurchaseOrder
from apps.vendors.models import VendorProfile
from apps.utils.enums import POStatusEnum, QualityRatingEnum, UserGroup


User = get_user_model()


class VendorApiTest(TestCase):
    """ Tests vendor profile endpoints"""
    
    endpoint = "/api/vendors/"
    login_endpoint = "/api/auth/login/"
    faker = Faker()
    current_date = datetime.now()

    def setUp(self):
        self.client = APIClient()
        self.no_auth_client = APIClient()

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

        self.user = User.objects.create(**self.user_payload)
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

        self.second_vendor_payload = dict(
            first_name="Mark",
            last_name="Grayson",
            email="invincible@gmail.com",
            mobile="08139572100",
            password="$rootpa$$",
            username="invincible",
            address="221B Baker Street",
            state="NY",
            country="USA",
            city="New York",
            postal_code="10001",
        )

        self.vendor_user = User.objects.create(**self.vendor_payload)
        self.vendor_user.set_password(self.vendor_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
        self.user.groups.add(self.group)
        self.user.save()


        self.second_vendor_user = User.objects.create(**self.second_vendor_payload)
        self.vendor_user.set_password(self.second_vendor_payload.get("password"))
        self.group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
        self.user.groups.add(self.group)
        self.user.save()

        # create a new vendor
        self.vendor_data = dict(
            ref_code =  "123234",
            user=self.vendor_user
        )

        self.second_vendor_data = dict(
            ref_code =  "1232342",
            user=self.second_vendor_user
        )

        self.first_vendor = VendorProfile.objects.create(**self.vendor_data)
        
        self.second_vendor = VendorProfile.objects.create(**self.second_vendor_data)
        
        self.first_po_data = dict(
            buyer = self.first_vendor,
            po_number = "123234",
            vendor= self.first_vendor,
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
        self.second_po_data = dict(
            buyer = self.user,
            po_number = "122133",
            vendor= self.first_vendor,
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
        self.second_po = PurchaseOrder.objects.create(**self.second_po_data)
        self.first_po = PurchaseOrder.objects.create(**self.first_po_data)

        
        # Authenticate user
        self.response_buyer = self.client.post(
            f"{self.login_endpoint}",
            {"username": self.user_payload["email"], "password": self.user_payload["password"]},
        )
        self.assertEqual(self.response_buyer.status_code, status.HTTP_200_OK)
        self.client.credentials(
            HTTP_AUTHORIZATION="Bearer " + self.response.data["token"]["access"]
        )

      
    def test_auth_po_list(self):
        """Test po list endpoint."""
        res = self.client.get(self.endpoint)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_auth_create_po(self):
        """Test creating a po."""
        res = self.client.post(self.endpoint, self.first_po_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_auth_create_po_duplicate(self):
        """Test creating po duplicate."""
        res = self.client.post(self.endpoint, self.first_po_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        duplicate_res = self.client.post(self.endpoint, self.first_po_data)
        self.assertEqual(duplicate_res.status_code, status.HTTP_409_CONFLICT)


    def test_auth_update_po(self):
        """Test updating po by id."""
        
        res = self.client.put(f"{self.endpoint}{self.first_po.id}/", self.second_po_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)
        self.assertEqual(res.data["data"].get("id"), self.first_po.id)

    def test_auth_vendor_profile_details(self):
        """Test retrieving a po."""
        res = self.client.get(f"{self.endpoint}{self.first_po.id}/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data)

    def test_auth_delete_po(self):
        """Test deleting a po."""
        res = self.client.delete(f"{self.endpoint}{self.first_po.id}/")
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_no_auth_po_list_access(self):
        """Test unauthenticated po list."""
        res = self.no_auth_client.get(self.endpoint)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_auth_create_po(self):
        """Test unauthenticated user po creation."""
        res = self.no_auth_client.post(self.endpoint, self.second_po_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_auth_update_po(self):
        """Test unauthenticated po update."""
        res = self.no_auth_client.put(f"{self.endpoint}{self.second_po.id}/", self.first_po_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_auth_vendor_po_get(self):
        """Test unauthenticated po details."""
        res = self.no_auth_client.get(f"{self.endpoint}{self.second_po.id}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_auth_delete_po(self):
        """Test unauthenticated po deletion."""
        res = self.no_auth_client.delete(f"{self.endpoint}{self.second_po.id}/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)