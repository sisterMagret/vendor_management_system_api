from .conftest import buyer, vendor, po_data,  vendor_auth_client, buyer_auth_client
from rest_framework import status

endpoint = "/api/vendors/"

    
def test_auth_po_list(vendor_auth_client):
    """Test po list endpoint."""
    res = vendor_auth_client.get(endpoint)

    for r in res.data["data"]:
        assert r["vendor"] == vendor.id
    assert res.status_code == status.HTTP_200_OK


def test_auth_create_po(vendor_auth_client, po_data):
    """Test creating a po."""
    po1, _ = po_data
    res = vendor_auth_client.post(endpoint, po1)
    assert res.status_code == status.HTTP_201_CREATED


def test_auth_create_po_duplicate(vendor_auth_client, po_data):
    """Test creating po duplicate."""
    po1, _ = po_data
    res = vendor_auth_client.post(endpoint, po1)
    assert res.status_code == status.HTTP_201_CREATED

    duplicate_res = vendor_auth_client.post(endpoint, po1)
    assert duplicate_res.status_code, status.HTTP_409_CONFLICT


def test_auth_update_po(vendor_auth_client, po_data, po_instances):
    """Test updating po by id."""
    po1, po2 = po_data
    inst1, _ = po_instances
    res = vendor_auth_client.put(f"{endpoint}{inst1.id}/", po2)
    assert res.status_code == status.HTTP_200_OK
    assert res.data
    assert res.data["data"].get("id"), po1.id


def test_auth_po_details(vendor_auth_client, po_instances):
    """Test retrieving a po."""
    inst1, _ = po_instances
    res = vendor_auth_client.get(f"{endpoint}{inst1.id}/")
    assert res.status_code == status.HTTP_200_OK


def test_auth_delete_po(vendor_auth_client, po_instances):
    """Test deleting a po."""
    inst1, _ = po_instances
    res = vendor_auth_client.delete(f"{endpoint}{inst1.id}/")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_no_auth_po_list_access(client):
    """Test unauthenticated po list."""
    res = client.get(endpoint)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_create_po(client, po_data):
    """Test unauthenticated user po creation."""
    po1, _ = po_data
    res = client.post(endpoint, po1)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_update_po(client, po_data, po_instances):
    """Test unauthenticated po update."""
    _, po2 = po_data
    inst1, _ = po_instances
    res = client.put(f"{endpoint}{inst1.id}/", po2)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_vendor_po_get(client, po_instances):
    """Test unauthenticated po details."""
    inst1, _ = po_instances
    res = client.get(f"{endpoint}{inst1.id}/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_no_auth_delete_po(client, po_instances):
    """Test unauthenticated po deletion."""
    inst1, _ = po_instances
    res = client.delete(f"{endpoint}{inst1.id}/")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED
