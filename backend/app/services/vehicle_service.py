import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import vehicle_repository
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.core.enums import VehicleStatus, VehicleType
from app.models.vehicle import Vehicle

def create_vehicle(db: Session, vehicle_in: VehicleCreate) -> Vehicle:
    """Validate registration number uniqueness and create a vehicle."""
    existing = vehicle_repository.get_vehicle_by_registration(db, vehicle_in.registration_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate registration number. A vehicle with this registration already exists."
        )
    return vehicle_repository.create_vehicle(db, vehicle_in)

def get_vehicle(db: Session, vehicle_id: uuid.UUID) -> Vehicle:
    """Retrieve a vehicle by ID, raising 404 if not found."""
    vehicle = vehicle_repository.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID '{vehicle_id}' not found."
        )
    return vehicle

def get_all_vehicles(
    db: Session,
    status: VehicleStatus | None = None,
    vehicle_type: VehicleType | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "asc"
) -> tuple[list[Vehicle], int]:
    """Retrieve filtered and sorted vehicles list."""
    return vehicle_repository.get_all_vehicles(
        db, status, vehicle_type, search, page, limit, sort_by, order
    )

def update_vehicle(db: Session, vehicle_id: uuid.UUID, vehicle_in: VehicleUpdate) -> Vehicle:
    """Update a vehicle, ensuring any changed registration number is not a duplicate."""
    db_vehicle = get_vehicle(db, vehicle_id)
    
    if vehicle_in.registration_number:
        existing = vehicle_repository.get_vehicle_by_registration(db, vehicle_in.registration_number)
        if existing and existing.id != vehicle_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate registration number. This registration number is already in use by another vehicle."
            )
            
    return vehicle_repository.update_vehicle(db, db_vehicle, vehicle_in)

def delete_vehicle(db: Session, vehicle_id: uuid.UUID) -> None:
    """Delete a vehicle, preventing deletion if it is currently ON_TRIP."""
    db_vehicle = get_vehicle(db, vehicle_id)
    
    if db_vehicle.status == VehicleStatus.ON_TRIP:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle cannot be deleted because it is On Trip."
        )
        
    vehicle_repository.delete_vehicle(db, db_vehicle)
