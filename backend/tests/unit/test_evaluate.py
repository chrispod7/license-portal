from datetime import UTC, datetime, timedelta

from app.models import License, LicenseStatus, Product
from app.services import evaluate

NOW = datetime(2026, 1, 1, tzinfo=UTC)


def make(status=LicenseStatus.ACTIVE, expires_at=None, sku="ACME"):
    return License(key="x", status=status, expires_at=expires_at, product=Product(sku=sku, name="Acme"))


def test_missing_license():
    assert evaluate(None, NOW).reason == "not_found"


def test_active_perpetual_license_is_valid():
    assert evaluate(make(), NOW).valid


def test_active_unexpired_license_is_valid():
    assert evaluate(make(expires_at=NOW + timedelta(days=1)), NOW).valid


def test_expired_license():
    r = evaluate(make(expires_at=NOW - timedelta(seconds=1)), NOW)
    assert (r.valid, r.reason) == (False, "expired")


def test_expiry_boundary_is_exclusive():
    assert evaluate(make(expires_at=NOW), NOW).reason == "expired"


def test_revoked_license():
    assert evaluate(make(status=LicenseStatus.REVOKED), NOW).reason == "revoked"


def test_revoked_takes_priority_over_expired():
    lic = make(status=LicenseStatus.REVOKED, expires_at=NOW - timedelta(days=1))
    assert evaluate(lic, NOW).reason == "revoked"


def test_sku_must_match_when_given():
    assert evaluate(make(sku="ACME"), NOW, sku="OTHER").reason == "wrong_product"
    assert evaluate(make(sku="ACME"), NOW, sku="acme").valid
