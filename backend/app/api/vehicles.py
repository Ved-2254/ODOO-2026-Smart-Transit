import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import VehicleStatus, VehicleType
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.schemas.cost_summary import VehicleCostSummary
from app.services import vehicle_service
from app.services import cost_summary_service

router = APIRouter(prefix="/api/v1/vehicles", tags=["vehicles"])

# Access control dependencies
write_guard = Depends(require_roles("Fleet Manager", "Admin"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Safety Officer", "Financial Analyst"))

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new vehicle record. Allowed roles: Fleet Manager, Admin."""
    return vehicle_service.create_vehicle(db, vehicle_in)

@router.get("/", response_model=VehicleListResponse)
def list_vehicles(
    status: VehicleStatus | None = Query(None),
    vehicle_type: VehicleType | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("asc"),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """
    Retrieve vehicles with support for pagination, sorting, filtering, and search.
    Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst.
    """
    # Enforce allowed sort options
    allowed_sort_options = [
        "registration_number",
        "vehicle_name",
        "acquisition_cost",
        "odometer",
        "created_at"
    ]
    if sort_by not in allowed_sort_options:
        sort_by = "created_at"
        
    if order not in ["asc", "desc"]:
        order = "asc"
        
    items, total = vehicle_service.get_all_vehicles(
        db,
        status=status,
        vehicle_type=vehicle_type,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    
    return VehicleListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total
    )

@router.get("/{vehicle_id}/cost-summary", response_model=VehicleCostSummary)
def get_vehicle_cost_summary(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Get operational cost summary for a vehicle. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    return cost_summary_service.get_vehicle_cost_summary(db, vehicle_id)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve details of a specific vehicle. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    return vehicle_service.get_vehicle(db, vehicle_id)

@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: uuid.UUID,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update details of a specific vehicle. Allowed roles: Fleet Manager, Admin."""
    return vehicle_service.update_vehicle(db, vehicle_id, vehicle_in)

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete a vehicle record. Allowed roles: Fleet Manager, Admin. Rejects if vehicle status is ON_TRIP."""
    vehicle_service.delete_vehicle(db, vehicle_id)
