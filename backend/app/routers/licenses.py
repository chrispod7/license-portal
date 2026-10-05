from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import services
from app.config import Settings, get_settings
from app.database import get_db
from app.models import License, LicenseStatus
from app.schemas import LicenseIssue, LicenseOut, LicenseRevoke, ValidateRequest, ValidateResponse

router = APIRouter(prefix="/licenses", tags=["licenses"])


def _query():
    return select(License).options(joinedload(License.user), joinedload(License.product))


@router.get("", response_model=list[LicenseOut])
def list_licenses(
    user_id: int | None = None,
    product_id: int | None = None,
    status_: LicenseStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    q = _query().order_by(License.id.desc())
    if user_id is not None:
        q = q.where(License.user_id == user_id)
    if product_id is not None:
        q = q.where(License.product_id == product_id)
    if status_ is not None:
        q = q.where(License.status == status_)
    return db.scalars(q).all()


@router.get("/{license_id}", response_model=LicenseOut)
def get_license(license_id: int, db: Session = Depends(get_db)):
    lic = db.scalar(_query().where(License.id == license_id))
    if lic is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"License {license_id} not found")
    return lic


@router.post("", response_model=LicenseOut, status_code=status.HTTP_201_CREATED)
def issue_license(body: LicenseIssue, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    return services.issue_license(db, body.user_id, body.product_id, body.expires_at, settings.license_signing_secret)


@router.post("/{license_id}/revoke", response_model=LicenseOut)
def revoke_license(license_id: int, body: LicenseRevoke, db: Session = Depends(get_db)):
    return services.revoke_license(db, license_id, body.reason)


@router.post("/validate", response_model=ValidateResponse)
def validate_license(body: ValidateRequest, db: Session = Depends(get_db), settings: Settings = Depends(get_settings)):
    """Check a key. Always returns 200; `valid` and `reason` carry the verdict."""
    result, lic = services.validate_key(db, body.key, body.sku, settings.license_signing_secret)
    if not result.valid:
        return ValidateResponse(valid=False, reason=result.reason)
    return ValidateResponse(
        valid=True, license_id=lic.id, product_sku=lic.product.sku, expires_at=lic.expires_at
    )
