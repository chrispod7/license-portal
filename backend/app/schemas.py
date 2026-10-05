from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import LicenseStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# --- Users -------------------------------------------------------------------

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    created_at: datetime


# --- Products ----------------------------------------------------------------

class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=16, pattern=r"^[A-Za-z0-9]+$")
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class ProductOut(ORMModel):
    id: int
    sku: str
    name: str
    description: str | None
    created_at: datetime


# --- Licenses ----------------------------------------------------------------

class LicenseIssue(BaseModel):
    user_id: int
    product_id: int
    expires_at: datetime | None = Field(default=None, description="Omit for a perpetual license")


class LicenseRevoke(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class LicenseOut(ORMModel):
    id: int
    key: str
    user_id: int
    product_id: int
    status: LicenseStatus
    is_expired: bool
    issued_at: datetime
    expires_at: datetime | None
    revoked_at: datetime | None
    revoke_reason: str | None
    user: UserOut
    product: ProductOut


class ValidateRequest(BaseModel):
    key: str
    sku: str | None = Field(default=None, description="If given, the key must belong to this product")


class ValidateResponse(BaseModel):
    valid: bool
    reason: str | None = None
    license_id: int | None = None
    product_sku: str | None = None
    expires_at: datetime | None = None
