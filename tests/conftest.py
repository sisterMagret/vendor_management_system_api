from datetime import datetime
import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from faker import Faker


from apps.purchase_orders.models import PurchaseOrder
from apps.utils.enums import POStatusEnum, QualityRatingEnum, UserGroup
from apps.vendors.models import VendorProfile

User = get_user_model()
faker = Faker()
current_date = datetime.now()

@pytest.fixture
def user_payload() -> dict:
    """
    Function to create a user payload.
    RETURN: dict
    """
    data = dict(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            mobile=faker.phone_number(),
            password="$rootpa$$",
            username="john_doe",
            address=faker.address(),
            state="NY",
            country="USA",
            city="New York",
            postal_code="10001",
        )
    return data


@pytest.fixture
def buyer(user_payload) -> tuple:
    """
    Fixture to create a user.
    """
    user = User.objects.create(**user_payload)
    user.set_password(user_payload.get("password"))
    group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
    user.groups.add(group)
    user.save()
    return user


@pytest.fixture
def second_buyer(user_payload) -> tuple:
    """
    Fixture to create a second user.
    """
    user_payload.update(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        mobile=faker.phone_number(),
        password="$rootpa$$",
        username=faker.user_name(),
        address=faker.address(),
    )
    user = User.objects.create(**user_payload)
    user.set_password(user_payload.get("password"))
    group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
    user.groups.add(group)
    user.save()
    return user


@pytest.fixture
def vendor(user_payload) -> VendorProfile:
    """
    Fixture to create a user.
    """
    user_payload.update(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        mobile=faker.phone_number(),
        password="$rootpa$$",
        username=faker.user_name(),
    )
    user = User.objects.create(**user_payload)
    user.set_password(user_payload.get("password"))
    group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
    user.groups.add(group)
    user.save()

    vendor_data = dict(
        ref_code= "123234",
        user=user
    )
    vendor = VendorProfile.objects.create(**vendor_data)
    assert len(vendor.ref_code) == 6
    return vendor


@pytest.fixture
def second_vendor(user_payload) -> VendorProfile:
    """
    Fixture to create a user.
    """
    user_payload.update(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        mobile=faker.phone_number(),
        password="$rootpa$$",
        username=faker.user_name(),
    )
    user = User.objects.create(**user_payload)
    user.set_password(user_payload.get("password"))
    group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
    user.groups.add(group)
    user.save()

    vendor_data = dict(
        ref_code= "245325",
        user=user
    )
    vendor = VendorProfile.objects.create(**vendor_data)
    assert len(vendor.ref_code) == 6
    return vendor


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def buyer_auth_client(buyer, client):
    """
    Fixture to create an authenticated API client.
    """
    endpoint = "/api/auth/"
    # Create a user
   
    # Authenticate the client
    auth_client = client.post(
            f"{endpoint}login/",
            dict(
                username=buyer.email, password=buyer.password,
            ),
        )
    assert auth_client.status_code == 200
    assert auth_client["token"]
    assert auth_client["data"]

    auth_client.credentials(
        HTTP_AUTHORIZATION="Bearer " + auth_client.data["token"]["access"]
    )
    return auth_client


@pytest.fixture
def vendor_auth_client(vendor, client):
    """
    Fixture to create an authenticated API client.
    """
    endpoint = "/api/auth/"
    # Create a user
   
    # Authenticate the client
    auth_client = client.post(
            f"{endpoint}login/",
            dict(
                username=vendor.user.mobile, password=vendor.user.password,
            ),
        )
    assert auth_client.status_code == 200 
    assert auth_client["token"]
    assert auth_client["data"] 

    auth_client.credentials(
        HTTP_AUTHORIZATION="Bearer " + auth_client.data["token"]["access"]
    )
    return auth_client

@pytest.fixture
def po_data(buyer, second_buyer, vendor):
    first_po_data = dict(
        buyer = buyer,
        po_number = "123234234567",
        vendor= vendor,
        order_date = current_date.strftime("%d:%m:%Y %H:%M:%S"),
        delivery_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        items = ["playstation 5", "mc book"],
        quantity = 2,
        status= POStatusEnum.PENDING,
        total_amount= 100000,
        quality_rating = QualityRatingEnum.FIVE,
        issue_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        acknowledgment_date=current_date.strftime("%d:%m:%Y %H:%M:%S"),
    )

    second_po_data = dict(
        buyer = second_buyer,
        po_number = "122133234567",
        vendor= vendor,
        order_date = current_date.strftime("%d:%m:%Y %H:%M:%S"),
        delivery_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        items = ["playstation 5", "mc book"],
        quantity = 2,
        status= POStatusEnum.PENDING,
        total_amount= 100000,
        quality_rating = QualityRatingEnum.FIVE,
        issue_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        acknowledgment_date=current_date.strftime("%d:%m:%Y %H:%M:%S"),
    )

    return first_po_data, second_po_data

@pytest.fixture
def po_instances(po_data) -> tuple:
   
    first_po_data,  second_po_data = po_data
    second_po = PurchaseOrder.objects.create(**second_po_data)
    first_po = PurchaseOrder.objects.create(**first_po_data)

    assert len(first_po.po_number) == 12
    assert len(second_po.po_number) == 12

    return first_po, second_po
