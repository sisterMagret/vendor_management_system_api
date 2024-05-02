from .conftest import buyer, vendor, po_data, user_payload, vendor_auth_client, buyer_auth_client
from rest_framework import status


endpoint = "/api/vendors/"


def test_auth_vendor_profile_list(vendor_auth_client):
    """Test authenticated vendor profile list."""
    res = vendor_auth_client.get(endpoint)
    assert res.status_code == status.HTTP_200_OK
   

def test_auth_create_vendor_profile(vendor_auth_client, user_payload):
    """Test creating a vendor profile."""
    user_payload.update(
        ref_code= "123234",
    )
    res = vendor_auth_client.post(endpoint, user_payload)
    assert res.status_code == status.HTTP_201_CREATED


def test_auth_update_vendor_profile(vendor_auth_client, vendor):
    """Test updating a vendor profile."""
    user_payload = {
        "first_name": "Sister",
        "last_name": "Magret",
    }
    res = vendor_auth_client.put(f"{endpoint}{vendor.id}/", user_payload)
    assert res.status_code == status.HTTP_200_OK
    assert res.data
    assert res.data["data"].get("first_name") == user_payload.get("first_name")


def test_auth_vendor_profile_details(vendor_auth_client, vendor):
    """Test retrieving a vendor profile."""
    res = vendor_auth_client.get(f"{endpoint}{vendor.id}/")
    assert res.status_code == status.HTTP_200_OK
    assert res.data


def test_auth_delete_vendor_profile(vendor_auth_client, vendor):
    """Test deleting a vendor profile."""
    res = vendor_auth_client.delete(f"{endpoint}{vendor.id}/")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_no_auth_vendor_profile_list(client):
    """Test unauthenticated vendor profile list."""
    res = client.get(endpoint)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_create_vendor_profile(client, user_payload):
    """Test unauthenticated vendor profile creation."""
    res = client.post(endpoint, user_payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_update_vendor_profile(client, vendor):
    """Test unauthenticated vendor profile update."""
    payload = {
        "first_name": "Sister",
        "last_name": "Magret",
    }
    res = client.put(f"{endpoint}{vendor.id}/", payload)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_vendor_profile_details(client, vendor):
    """Test unauthenticated vendor profile details."""
    res = client.get(f"{endpoint}{vendor.id}/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_delete_vendor_profile(client, vendor):
        """Test unauthenticated vendor profile deletion."""
        res = client.delete(f"{endpoint}{vendor.id}/")
        assert res.status_code == status.HTTP_401_UNAUTHORIZED