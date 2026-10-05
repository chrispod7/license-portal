from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import update

from app.database import engine
from app.models import License

pytestmark = pytest.mark.integration


def test_issue_license(client, license_, user, product):
    assert license_["key"].startswith("ACME-")
    assert license_["status"] == "active"
    assert license_["is_expired"] is False
    assert license_["user"]["email"] == user["email"]
    assert license_["product"]["sku"] == product["sku"]


def test_issue_for_missing_user_or_product_is_404(client, user, product):
    assert client.post("/api/licenses", json={"user_id": 999, "product_id": product["id"]}).status_code == 404
    assert client.post("/api/licenses", json={"user_id": user["id"], "product_id": 999}).status_code == 404


def test_issue_with_past_expiry_is_rejected(client, user, product):
    past = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    r = client.post("/api/licenses", json={"user_id": user["id"], "product_id": product["id"], "expires_at": past})
    assert r.status_code == 409


def test_validate_active_key(client, license_):
    r = client.post("/api/licenses/validate", json={"key": license_["key"], "sku": "ACME"})
    assert r.json() == {
        "valid": True,
        "reason": None,
        "license_id": license_["id"],
        "product_sku": "ACME",
        "expires_at": None,
    }


def test_validate_rejects_malformed_and_unknown_keys(client, license_):
    assert client.post("/api/licenses/validate", json={"key": "junk"}).json()["reason"] == "malformed"
    # Correctly shaped but with a broken checksum
    k = license_["key"]
    forged = k[:-1] + ("0" if k[-1] != "0" else "1")
    assert client.post("/api/licenses/validate", json={"key": forged}).json()["reason"] == "malformed"


def test_validate_wrong_product(client, license_):
    r = client.post("/api/licenses/validate", json={"key": license_["key"], "sku": "OTHER"})
    assert r.json()["reason"] == "wrong_product"


def test_revoke_then_validate(client, license_):
    r = client.post(f"/api/licenses/{license_['id']}/revoke", json={"reason": "chargeback"})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "revoked"
    assert body["revoke_reason"] == "chargeback"
    assert body["revoked_at"] is not None

    r = client.post("/api/licenses/validate", json={"key": license_["key"]})
    assert r.json() == {
        "valid": False,
        "reason": "revoked",
        "license_id": None,
        "product_sku": None,
        "expires_at": None,
    }


def test_double_revoke_is_conflict(client, license_):
    client.post(f"/api/licenses/{license_['id']}/revoke", json={})
    assert client.post(f"/api/licenses/{license_['id']}/revoke", json={}).status_code == 409


def test_expired_license_fails_validation(client, license_):
    # Backdate expiry directly in the DB; the API won't issue already-expired keys.
    with engine.begin() as conn:
        conn.execute(
            update(License)
            .where(License.id == license_["id"])
            .values(expires_at=datetime.now(UTC) - timedelta(minutes=1))
        )
    assert client.post("/api/licenses/validate", json={"key": license_["key"]}).json()["reason"] == "expired"
    assert client.get(f"/api/licenses/{license_['id']}").json()["is_expired"] is True


def test_list_filters(client, user, product):
    other = client.post("/api/products", json={"sku": "BETA", "name": "Beta"}).json()
    a = client.post("/api/licenses", json={"user_id": user["id"], "product_id": product["id"]}).json()
    client.post("/api/licenses", json={"user_id": user["id"], "product_id": other["id"]})
    client.post(f"/api/licenses/{a['id']}/revoke", json={})

    assert len(client.get("/api/licenses").json()) == 2
    assert len(client.get(f"/api/licenses?product_id={other['id']}").json()) == 1
    revoked = client.get("/api/licenses?status=revoked").json()
    assert [lic["id"] for lic in revoked] == [a["id"]]
