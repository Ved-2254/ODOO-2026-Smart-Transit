import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import MaintenanceStatus
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse, MaintenanceListResponse
from app.services import maintenance_service

router = APIRouter(prefix="/api/v1/maintenance", tags=["maintenance"])

# Access control guards
write_guard = Depends(require_roles("Fleet Manager", "Admin"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Safety Officer", "Financial Analyst"))

@router.post("/", response_model=MaintenanceResponse, status_code=status.HTTP_201_CREATED)
def create_maintenance_log(
    log_in: MaintenanceCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new maintenance record. Allowed roles: Fleet Manager, Admin."""
    return maintenance_service.create_maintenance_log(db, log_in)

@router.get("/", response_model=MaintenanceListResponse)
def list_maintenance_logs(
    status: MaintenanceStatus | None = Query(None),
    vehicle_id: uuid.UUID | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """List maintenance records. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    items, total = maintenance_service.get_all_logs(db, status=status, vehicle_id=vehicle_id, page=page, limit=limit)
    return MaintenanceListResponse(items=items, page=page, limit=limit, total=total)

@router.get("/{log_id}", response_model=MaintenanceResponse)
def get_maintenance_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve details of a maintenance record. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    return maintenance_service.get_maintenance_log(db, log_id)

@router.put("/{log_id}", response_model=MaintenanceResponse)
def update_maintenance_log(
    log_id: uuid.UUID,
    log_in: MaintenanceUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update a maintenance record. Allowed roles: Fleet Manager, Admin."""
    return maintenance_service.update_maintenance_log(db, log_id, log_in)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete a maintenance record. Allowed roles: Fleet Manager, Admin."""
    maintenance_service.delete_maintenance_log(db, log_id)

@router.post("/{log_id}/close", response_model=MaintenanceResponse)
def close_maintenance_log(
    log_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Close a maintenance record. Allowed roles: Fleet Manager, Admin."""
    return maintenance_service.close_maintenance_log(db, log_id)
