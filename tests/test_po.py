from rest_framework import status

endpoint = "/api/v1/vendors/purchase-order/"


def test_auth_po_list(vendor_auth_client, vendor):
    """Test po list endpoint."""
    res = vendor_auth_client.get(endpoint)
    if res.data["data"]["results"]:
        for r in res.data["data"]["results"]:
            assert r["vendor"]["id"] == vendor.id

    assert res.status_code == status.HTTP_200_OK


