import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import TripStatus

class TripBase(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    cargo_weight: float = Field(..., gt=0)
    planned_distance: float = Field(..., gt=0)

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    source: str | None = Field(None, min_length=1, max_length=255)
    destination: str | None = Field(None, min_length=1, max_length=255)
    vehicle_id: uuid.UUID | None = None
    driver_id: uuid.UUID | None = None
    cargo_weight: float | None = Field(None, gt=0)
    planned_distance: float | None = Field(None, gt=0)

class TripCompleteInput(BaseModel):
    final_odometer: float = Field(..., gt=0)
    fuel_consumed: float = Field(..., gt=0)

class TripResponse(BaseModel):
    id: uuid.UUID
    source: str
    destination: str
    vehicle_id: uuid.UUID
    driver_id: uuid.UUID
    cargo_weight: float
    planned_distance: float
    final_odometer: float | None = None
    fuel_consumed: float | None = None
    status: TripStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TripListResponse(BaseModel):
    items: list[TripResponse]
    page: int
    limit: int
    total: int
