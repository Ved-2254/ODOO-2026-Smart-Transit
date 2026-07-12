import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import DriverStatus, LicenseCategory
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse, DriverListResponse
from app.services import driver_service

router = APIRouter(prefix="/api/v1/drivers", tags=["drivers"])

# Access control guards
write_guard = Depends(require_roles("Fleet Manager", "Admin"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Safety Officer", "Financial Analyst"))

@router.post("/", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def create_driver(
    driver_in: DriverCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new driver. Allowed roles: Fleet Manager, Admin."""
    return driver_service.create_driver(db, driver_in)

@router.get("/", response_model=DriverListResponse)
def list_drivers(
    status: DriverStatus | None = Query(None),
    license_category: LicenseCategory | None = Query(None),
    expired: bool | None = Query(None),
    safety_score_min: int | None = Query(None, ge=0, le=100),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """
    Retrieve paginated drivers matching filters.
    Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst.
    """
    # Enforce allowed sort options
    allowed_sorts = ["full_name", "safety_score", "license_expiry_date", "created_at"]
    if sort_by not in allowed_sorts:
        sort_by = "created_at"
        
    if order not in ["asc", "desc"]:
        order = "asc"
        
    items, total = driver_service.get_all_drivers(
        db,
        status=status,
        license_category=license_category,
        expired=expired,
        safety_score_min=safety_score_min,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    
    return DriverListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total
    )

@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve details of a driver. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    return driver_service.get_driver(db, driver_id)

@router.put("/{driver_id}", response_model=DriverResponse)
def update_driver(
    driver_id: uuid.UUID,
    driver_in: DriverUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update details of a driver. Allowed roles: Fleet Manager, Admin."""
    return driver_service.update_driver(db, driver_id, driver_in)

@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(
    driver_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete a driver record. Allowed roles: Fleet Manager, Admin. Rejects if driver status is ON_TRIP."""
    driver_service.delete_driver(db, driver_id)
