import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class FuelLogCreate(BaseModel):
    vehicle_id: uuid.UUID
    trip_id: uuid.UUID | None = None
    fuel_date: datetime
    liters: float = Field(..., gt=0, description="Fuel quantity in liters, must be > 0")
    cost: float = Field(..., ge=0, description="Total fuel cost, must be >= 0")
    odometer: float = Field(..., ge=0, description="Odometer reading at fill-up")


class FuelLogUpdate(BaseModel):
    trip_id: uuid.UUID | None = None
    fuel_date: datetime | None = None
    liters: float | None = Field(None, gt=0)
    cost: float | None = Field(None, ge=0)
    odometer: float | None = Field(None, ge=0)


class FuelLogResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    trip_id: uuid.UUID | None = None
    fuel_date: datetime
    liters: float
    cost: float
    odometer: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FuelLogListResponse(BaseModel):
    items: list[FuelLogResponse]
    page: int
    limit: int
    total: int
