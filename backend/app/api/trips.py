import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import TripStatus
from app.schemas.trip import TripCreate, TripUpdate, TripCompleteInput, TripResponse, TripListResponse
from app.services import trip_service

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])

# Access control guards
write_guard = Depends(require_roles("Fleet Manager", "Admin"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Safety Officer", "Financial Analyst"))

@router.post("/", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip_in: TripCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new trip. Allowed roles: Fleet Manager, Admin."""
    return trip_service.create_trip(db, trip_in)

@router.get("/", response_model=TripListResponse)
def list_trips(
    status: TripStatus | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """List trips. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    items, total = trip_service.get_all_trips(db, status=status, page=page, limit=limit)
    return TripListResponse(items=items, page=page, limit=limit, total=total)

@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve details of a trip. Allowed roles: Fleet Manager, Admin, Safety Officer, Financial Analyst."""
    return trip_service.get_trip(db, trip_id)

@router.put("/{trip_id}", response_model=TripResponse)
def update_trip(
    trip_id: uuid.UUID,
    trip_in: TripUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update details of a draft trip. Allowed roles: Fleet Manager, Admin."""
    return trip_service.update_trip(db, trip_id, trip_in)

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete a trip (only allowed in DRAFT or CANCELLED status). Allowed roles: Fleet Manager, Admin."""
    trip_service.delete_trip(db, trip_id)

@router.post("/{trip_id}/dispatch", response_model=TripResponse)
def dispatch_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Dispatch a trip. Updates status to DISPATCHED. Allowed roles: Fleet Manager, Admin."""
    return trip_service.dispatch_trip(db, trip_id)

@router.post("/{trip_id}/complete", response_model=TripResponse)
def complete_trip(
    trip_id: uuid.UUID,
    complete_in: TripCompleteInput,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Complete a trip, recording final stats. Allowed roles: Fleet Manager, Admin."""
    return trip_service.complete_trip(db, trip_id, complete_in)

@router.post("/{trip_id}/cancel", response_model=TripResponse)
def cancel_trip(
    trip_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Cancel a trip. Allowed roles: Fleet Manager, Admin."""
    return trip_service.cancel_trip(db, trip_id)
