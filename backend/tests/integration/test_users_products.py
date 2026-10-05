import pytest

pytestmark = pytest.mark.integration


def test_user_crud(client):
    r = client.post("/api/users", json={"email": "Grace@Example.com", "full_name": "Grace Hopper"})
    assert r.status_code == 201
    user = r.json()
    assert user["email"] == "grace@example.com"

    assert client.get(f"/api/users/{user['id']}").json()["full_name"] == "Grace Hopper"
    assert len(client.get("/api/users").json()) == 1

    r = client.patch(f"/api/users/{user['id']}", json={"full_name": "Rear Adm. Grace Hopper"})
    assert r.json()["full_name"] == "Rear Adm. Grace Hopper"

    assert client.delete(f"/api/users/{user['id']}").status_code == 204
    assert client.get(f"/api/users/{user['id']}").status_code == 404


def test_duplicate_email_is_conflict(client, user):
    r = client.post("/api/users", json={"email": "ADA@example.com", "full_name": "Other"})
    assert r.status_code == 409


def test_invalid_email_is_rejected(client):
    assert client.post("/api/users", json={"email": "nope", "full_name": "X"}).status_code == 422


def test_product_crud(client):
    r = client.post("/api/products", json={"sku": "pro2", "name": "Pro", "description": "v2"})
    assert r.status_code == 201
    product = r.json()
    assert product["sku"] == "PRO2"

    r = client.patch(f"/api/products/{product['id']}", json={"name": "Pro Edition"})
    assert r.json()["name"] == "Pro Edition"

    assert client.delete(f"/api/products/{product['id']}").status_code == 204
    assert client.get(f"/api/products/{product['id']}").status_code == 404


def test_duplicate_sku_is_conflict(client, product):
    assert client.post("/api/products", json={"sku": "ACME", "name": "Again"}).status_code == 409


def test_cannot_delete_user_or_product_with_licenses(client, license_):
    assert client.delete(f"/api/users/{license_['user_id']}").status_code == 409
    assert client.delete(f"/api/products/{license_['product_id']}").status_code == 409
