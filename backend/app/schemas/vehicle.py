import uuid
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import VehicleStatus, VehicleType

class VehicleBase(BaseModel):
    registration_number: str = Field(..., min_length=1, max_length=50)
    vehicle_name: str = Field(..., min_length=1, max_length=100)
    vehicle_model: str = Field(..., min_length=1, max_length=100)
    vehicle_type: VehicleType
    maximum_load_capacity: float = Field(..., gt=0)
    odometer: float = Field(..., ge=0)
    acquisition_cost: Decimal = Field(..., ge=0)
    status: VehicleStatus

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    registration_number: str | None = Field(None, min_length=1, max_length=50)
    vehicle_name: str | None = Field(None, min_length=1, max_length=100)
    vehicle_model: str | None = Field(None, min_length=1, max_length=100)
    vehicle_type: VehicleType | None = None
    maximum_load_capacity: float | None = Field(None, gt=0)
    odometer: float | None = Field(None, ge=0)
    acquisition_cost: Decimal | None = Field(None, ge=0)
    status: VehicleStatus | None = None

class VehicleResponse(BaseModel):
    id: uuid.UUID
    registration_number: str
    vehicle_name: str
    vehicle_model: str
    vehicle_type: VehicleType
    maximum_load_capacity: float
    odometer: float
    acquisition_cost: Decimal
    status: VehicleStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    page: int
    limit: int
    total: int
