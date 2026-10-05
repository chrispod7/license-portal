"""License business rules: issuing, revoking, validating."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import keys
from app.models import License, LicenseStatus, Product, User


class NotFound(Exception):
    pass


class Conflict(Exception):
    pass


@dataclass
class ValidationResult:
    valid: bool
    reason: str | None = None


def evaluate(lic: License | None, now: datetime, sku: str | None = None) -> ValidationResult:
    """Decide whether a license is currently usable. Pure: no I/O."""
    if lic is None:
        return ValidationResult(False, "not_found")
    if sku is not None and lic.product.sku != sku.upper():
        return ValidationResult(False, "wrong_product")
    if lic.status == LicenseStatus.REVOKED:
        return ValidationResult(False, "revoked")
    if lic.expires_at is not None and lic.expires_at <= now:
        return ValidationResult(False, "expired")
    return ValidationResult(True)


def issue_license(db: Session, user_id: int, product_id: int, expires_at: datetime | None, secret: str) -> License:
    user = db.get(User, user_id)
    if user is None:
        raise NotFound(f"User {user_id} not found")
    product = db.get(Product, product_id)
    if product is None:
        raise NotFound(f"Product {product_id} not found")
    if expires_at is not None:
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            raise Conflict("expires_at must be in the future")

    # Collisions are astronomically unlikely (32^15 keyspace per SKU), but cheap to guard.
    for _ in range(5):
        key = keys.generate_key(product.sku, secret)
        if db.scalar(select(License.id).where(License.key == key)) is None:
            break
    else:
        raise RuntimeError("Could not generate a unique license key")

    lic = License(key=key, user=user, product=product, expires_at=expires_at)
    db.add(lic)
    db.commit()
    db.refresh(lic)
    return lic


def revoke_license(db: Session, license_id: int, reason: str | None) -> License:
    lic = db.get(License, license_id)
    if lic is None:
        raise NotFound(f"License {license_id} not found")
    if lic.status == LicenseStatus.REVOKED:
        raise Conflict("License is already revoked")
    lic.status = LicenseStatus.REVOKED
    lic.revoked_at = datetime.now(UTC)
    lic.revoke_reason = reason
    db.commit()
    db.refresh(lic)
    return lic


def validate_key(db: Session, key: str, sku: str | None, secret: str) -> tuple[ValidationResult, License | None]:
    key = keys.normalize(key)
    if not keys.is_well_formed(key, secret):
        return ValidationResult(False, "malformed"), None
    lic = db.scalar(select(License).options(joinedload(License.product)).where(License.key == key))
    return evaluate(lic, datetime.now(UTC), sku), lic
