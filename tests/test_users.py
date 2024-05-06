# import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

from apps.users.models import BuyerSettings, VendorProfile
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


def test_vendor_model(db, new_user):
    vendor = VendorProfile.objects.create(
        business_name="Car supplies", user=new_user
    )
    assert VendorProfile.objects.all().count() == 1
    assert vendor.business_name == "Car supplies"


# def test_register_vendor(user_data, client):
#         """
#         test user buyer
#         """
#         user_data.update({
#             "business_name": "Sony",
#             "is_accept_terms_and_condition": True
#             })
#         response = client.post(
#                 f"{register_endpoint}{UserGroup.BUYER}",
#                 user_data, format="json",
#                 content_type="application/json"
#         )
#         assert response.status_code == status.HTTP_201_CREATED


def test_get_vendor_profile(vendor_auth_client):
    response = vendor_auth_client.get(f"/api/v1/vendors/profile/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["user"]["group"] == UserGroup.VENDOR


def test_delete_account(vendor_auth_client):
    response = vendor_auth_client.delete(f"/api/v1/users/delete/")
    assert response.status_code == status.HTTP_204_NO_CONTENT
   

def test_get_buyer_profile(buyer_auth_client):
    response = buyer_auth_client.get(f"/api/v1/buyers/profile/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["user"]["group"] == UserGroup.BUYER


def test_list_vendors(vendor_auth_client):
    response = vendor_auth_client.get(f"/api/v1/vendors/")
    assert response.status_code == status.HTTP_200_OK

# def test_list_buyer_vendors(buyer_auth_client):
#     response = buyer_auth_client.get(f"/api/v1/buyer/vendors/")
#     assert response.status_code == status.HTTP_200_OK

# def test_list_vendor_buyers(vendor_auth_client):
#     response = vendor_auth_client.get(f"/api/v1/vendor/buyers/")
#     print(response.json())
#     assert response.status_code == status.HTTP_200_OK

# def test_list_all_users(vendor_auth_client):
#     response = vendor_auth_client.get(f"/api/v1/users/")
#     assert response.status_code == status.HTTP_200_OK


# def test_refresh_tokens(buyer_auth_client):
#     auth_headers = buyer_auth_client.credentials()
#     print(auth_headers)
#     # assert auth_headers["HTTP_AUTHORIZATION"].startswith("Bearer ")
#     # response = vendor_auth_client.get(f"/api/v1/identity/refresh/")
#     # assert response.status_code == status.HTTP_200_OK
#     assert True