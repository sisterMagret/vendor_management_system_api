from .conftest import buyer, vendor, client
from rest_framework import status

endpoint = "/api/auth/login/"


def test_user_login_with_email(buyer, client):
    """
    Test making an authenticated request with email.
    """
    response = client.post(
            endpoint,
            dict(
                username=buyer.email, password=buyer.password
            ),
        )
    assert response.status_code == status.HTTP_200_OK
    assert response["token"]
    assert response["data"]


def test_user_login_with_mobile(vendor, client):
        """
        test user login with mobile number
        """
        response = client.post(
            endpoint,
            dict(
                username=vendor.user.mobile, password=vendor.user.password
            ),
        )
        assert response.status_code == status.HTTP_200_OK
        assert response["token"]
        assert response["data"]


def test_user_login_with_username(vendor, client):
    """
    test user login with username
    """
    response = client.post(
        endpoint,
        dict(
            username=vendor.user.username, password=vendor.user.password

        ),
    )

    assert response.status_code == status.HTTP_200_OK
    assert response["token"]
    assert response["data"]


def test_user_login_invalid_cred(vendor, client):
    """
    test user login with invalid credential
    """
    response = client.post(
        endpoint,
        dict(
            username=vendor.user.username, password="wrong password"
        ),
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response["data"] == "Invalid Credentials"


def test_user_model(user_payload):
        user = User.objects.create(username=user_payload.create(**user_payload.data))
        assert User.objects.all().count() == 1
        assert User.objects.filter(email=user.email).exists()
        