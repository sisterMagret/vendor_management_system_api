# import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.authentication.models import BuyerSettings
from apps.utils.enums import UserGroup

User = get_user_model()
register_endpoint = "/api/v1/auth/register/"
endpoint = "/api/v1/auth/login/"


def test_new_user(new_user):
    count = User.objects.all().count()
    assert count == 1


def test_buyer_settings(buyer):
    count = BuyerSettings.objects.all().count()
    assert count == 1


# def test_register_buyer(user_data, client):
#         """
#         test user buyer
#         """
#         user_data.update({
#             "business_name": "Sony",
#             "is_accept_terms_and_condition": True
#             })
#         response = client.post(
#             f"{register_endpoint}{UserGroup.BUYER}",
#             user_data, format="json",
#              content_type="application/json"
#         )
#         print(response.json())
#         assert response.status_code == status.HTTP_201_CREATED


def test_user_login_with_email(buyer, user_data, client):
    """
    Test making an authenticated request with email.
    """

    response = client.post(
        endpoint,
        dict(
            username=buyer.user.email, password=user_data.get("password")
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"]
    assert response.data["data"]


# def test_get_profile(buyer_auth_client):
#     response = buyer_auth_client.get(f"/api/v1/user/me/")
#     assert response.status_code == status.HTTP_200


def test_user_login_with_mobile(buyer, user_data, client):
    """
    test user login with mobile number
    """
    response = client.post(
        endpoint,
        dict(
            username=buyer.user.mobile, password=user_data.get("password")
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"]["access"]
    assert response.data["token"]["refresh"]
    assert response.data["data"]


def test_user_login_with_username(buyer, user_data, client):
    """
    test user login with username
    """
    response = client.post(
        endpoint,
        dict(
            username=buyer.user.username,
            password=user_data.get("password"),
        ),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["token"]
    assert response.data["data"]


def test_user_login_invalid_cred(buyer, client):
    """
    test user login with invalid credential
    """
    response = client.post(
        endpoint,
        dict(username=buyer.user.username, password="wrong password"),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["message"]
        == "Invalid credentials, Kindly supply valid credentials"
    )


def test_user_model(db, user_data):
    user = User.objects.create(**user_data)
    assert User.objects.all().count() == 1
    assert User.objects.filter(email=user.email).exists()


def test_buyer_model(db, user_data):
    user = User.objects.create(**user_data)
    assert User.objects.all().count() == 1
    assert User.objects.filter(email=user.email).exists()

    buyer = BuyerSettings.objects.create(
        business_name="Samsung", user=user
    )
    assert BuyerSettings.objects.all().count() == 1
    assert buyer.business_name == "Samsung"


# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Group
# from apps.authentication.models import BuyerSetting
# from apps.utils.enums import UserGroup
# from ..conftest import user_data, buyer , client#, vendor


# User =  get_user_model()


#
