import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.core.enums import DriverStatus, LicenseCategory

class DriverBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100)
    license_number: str = Field(..., min_length=1, max_length=50)
    license_category: LicenseCategory
    license_expiry_date: date
    contact_number: str = Field(..., min_length=10, max_length=15)
    safety_score: int = Field(..., ge=0, le=100)
    status: DriverStatus

    @field_validator("contact_number")
    @classmethod
    def validate_contact(cls, v: str) -> str:
        # Check that contact number contains 10-15 digits (allow optional leading '+')
        clean = v.lstrip('+')
        if not clean.isdigit() or len(clean) < 10 or len(clean) > 15:
            raise ValueError("Contact number must contain only digits and be between 10 and 15 digits long")
        return v

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    license_number: str | None = Field(None, min_length=1, max_length=50)
    license_category: LicenseCategory | None = None
    license_expiry_date: date | None = None
    contact_number: str | None = Field(None, min_length=10, max_length=15)
    safety_score: int | None = Field(None, ge=0, le=100)
    status: DriverStatus | None = None

    @field_validator("contact_number")
    @classmethod
    def validate_contact(cls, v: str | None) -> str | None:
        if v is None:
            return v
        clean = v.lstrip('+')
        if not clean.isdigit() or len(clean) < 10 or len(clean) > 15:
            raise ValueError("Contact number must contain only digits and be between 10 and 15 digits long")
        return v

class DriverResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    full_name: str
    license_number: str
    license_category: LicenseCategory
    license_expiry_date: date
    contact_number: str
    safety_score: int
    status: DriverStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DriverListResponse(BaseModel):
    items: list[DriverResponse]
    page: int
    limit: int
    total: int
