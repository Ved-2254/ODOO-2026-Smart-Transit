import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import MaintenanceStatus

class MaintenanceBase(BaseModel):
    vehicle_id: uuid.UUID
    maintenance_type: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    cost: float = Field(..., ge=0)
    start_date: date
    status: MaintenanceStatus = MaintenanceStatus.ACTIVE

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    maintenance_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=255)
    cost: float | None = Field(None, ge=0)
    start_date: date | None = None
    end_date: date | None = None
    status: MaintenanceStatus | None = None

class MaintenanceResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    maintenance_type: str
    description: str
    start_date: date
    end_date: date | None = None
    cost: float
    status: MaintenanceStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MaintenanceListResponse(BaseModel):
    items: list[MaintenanceResponse]
    page: int
    limit: int
    total: int
