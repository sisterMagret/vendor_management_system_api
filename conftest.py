from datetime import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from faker import Faker
from pytest_factoryboy import register
from rest_framework.test import APIClient

from apps.users.models import BuyerSettings
from apps.purchase_orders.models import PurchaseOrder
from apps.utils.enums import POStatusEnum, UserGroup
from apps.users.models import VendorProfile
from apps.utils.random_number_generator import unique_alpha_numeric_generator
from tests.factories import UserFactory

faker = Faker()
User = get_user_model()
current_date = datetime.now()

register(UserFactory)


@pytest.fixture
def client(db):
    return APIClient()


@pytest.fixture
def user_data() -> dict:
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
        zip_code="10001",
    )
    return data


@pytest.fixture
def new_user(db, user_factory):
    user = user_factory.create()
    return user


@pytest.fixture
def buyer(new_user) -> tuple:
    """
    Fixture to create a buyer.
    """
    new_user.set_password(new_user.password)
    group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
    new_user.groups.add(group)
    new_user.save()
    profile_payload = dict(business_name="Apple", user=new_user)
    instance = BuyerSettings.objects.create(**profile_payload)
    assert instance.business_name == profile_payload.get("business_name")
    return instance


@pytest.fixture
def second_buyer(new_user) -> tuple:
    """
    Fixture to create a second user.
    """
    new_user.set_password(new_user.password)
    group, _ = Group.objects.get_or_create(name=UserGroup.BUYER)
    new_user.groups.add(group)
    new_user.save()
    profile_payload = dict(business_name="Sony", user=new_user)
    instance = BuyerSettings.objects.create(**profile_payload)
    return instance


@pytest.fixture
def vendor(new_user) -> VendorProfile:
    """
    Fixture to create a user.
    """
    new_user.set_password(new_user.password)
    group, _ = Group.objects.get_or_create(name=UserGroup.VENDOR)
    new_user.groups.add(group)
    new_user.save()

    vendor_data = dict(
        vendor_code = unique_alpha_numeric_generator(VendorProfile, "vendor_code", 8),
        business_name = "Sister Magret's PUB",
        user=new_user
    )
    vendor = VendorProfile.objects.create(**vendor_data)
    assert len(vendor.vendor_code) == 8
    return vendor


@pytest.fixture
def vendor_auth_client(vendor, client, user_data):
    """
    Fixture to create an authenticated API client.
    """
    endpoint = "/api/v1/auth/login/"
    # Create a user

    # Authenticate the client
    auth_client = client.post(
            endpoint,
            dict(
                username=vendor.user.mobile, password=user_data.get("password"),
            ),
        )
    

    assert auth_client.status_code == 200
    assert auth_client.data["token"]
    assert auth_client.data["data"]
    client.credentials(
        HTTP_AUTHORIZATION="Bearer " + auth_client.data["token"]["access"]
    )
    
    return client


@pytest.fixture
def buyer_auth_client(buyer, client, user_data):
    """
    Fixture to create an authenticated API client.
    """
    endpoint = "/api/v1/auth/login/"
    # Create a user

    # Authenticate the client
    auth_client = client.post(
        endpoint,
        dict(
            username=buyer.user.email,
            password=user_data.get("password"),
        ),
    )
    assert auth_client.status_code == 200
    assert auth_client.data["token"]
    assert auth_client.data["data"]

    client.credentials(
        HTTP_AUTHORIZATION="Bearer " + auth_client.data["token"]["access"]
    )
    return client


@pytest.fixture
def po_data(buyer, vendor):
    po = dict(
        buyer = buyer.user,
        po_number = "123234234567",
        vendor= vendor,
        order_date = current_date.strftime("%d:%m:%Y %H:%M:%S"),
        delivery_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        items = ["playstation 5", "mc book"],
        quantity = 2,
        status= POStatusEnum.PENDING,
        total_amount= 100000,
        quality_rating = 3.4,
        issue_date= current_date.strftime("%d:%m:%Y %H:%M:%S"),
        acknowledgment_date=current_date.strftime("%d:%m:%Y %H:%M:%S"),
    )

    return po


@pytest.fixture
def po_instances(po_data) -> tuple:
    po = PurchaseOrder.objects.create(**po_data)
    assert len(po.po_number) == 12

    return po
