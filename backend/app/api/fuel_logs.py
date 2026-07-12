import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.schemas.fuel import FuelLogCreate, FuelLogUpdate, FuelLogResponse, FuelLogListResponse
from app.services import fuel_service

router = APIRouter(prefix="/api/v1/fuel-logs", tags=["fuel-logs"])

# Access control guards
write_guard = Depends(require_roles("Fleet Manager", "Admin", "Financial Analyst"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Financial Analyst", "Safety Officer"))


@router.post("/", response_model=FuelLogResponse, status_code=status.HTTP_201_CREATED)
def create_fuel_log(
    fuel_log_in: FuelLogCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new fuel log. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    return fuel_service.create_fuel_log(db, fuel_log_in)


@router.get("/", response_model=FuelLogListResponse)
def list_fuel_logs(
    vehicle_id: uuid.UUID | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """List fuel logs with optional filters. Allowed roles: Fleet Manager, Admin, Financial Analyst, Safety Officer."""
    items, total = fuel_service.get_all_fuel_logs(
        db, vehicle_id=vehicle_id, date_from=date_from, date_to=date_to,
        page=page, limit=limit
    )
    return FuelLogListResponse(items=items, page=page, limit=limit, total=total)


@router.get("/{fuel_log_id}", response_model=FuelLogResponse)
def get_fuel_log(
    fuel_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve a fuel log by ID. Allowed roles: Fleet Manager, Admin, Financial Analyst, Safety Officer."""
    return fuel_service.get_fuel_log(db, fuel_log_id)


@router.put("/{fuel_log_id}", response_model=FuelLogResponse)
def update_fuel_log(
    fuel_log_id: uuid.UUID,
    fuel_log_in: FuelLogUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update a fuel log. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    return fuel_service.update_fuel_log(db, fuel_log_id, fuel_log_in)


@router.delete("/{fuel_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_log(
    fuel_log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete a fuel log. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    fuel_service.delete_fuel_log(db, fuel_log_id)
