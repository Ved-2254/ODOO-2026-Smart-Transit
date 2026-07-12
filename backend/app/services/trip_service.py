import uuid
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories import trip_repository
from app.schemas.trip import TripCreate, TripUpdate, TripCompleteInput
from app.core.enums import TripStatus, VehicleStatus, DriverStatus, MaintenanceStatus
from app.models.trip import Trip
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.maintenance import MaintenanceLog

def validate_trip_entities(
    db: Session,
    vehicle_id: uuid.UUID,
    driver_id: uuid.UUID,
    cargo_weight: float,
    exclude_trip_id: uuid.UUID | None = None
):
    """Enforce vehicle & driver availability, licenses, and cargo capacities."""
    # 1. Fetch Vehicle
    stmt_v = select(Vehicle).where(Vehicle.id == vehicle_id)
    db_vehicle = db.execute(stmt_v).scalar_one_or_none()
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle does not exist."
        )
        
    # 2. Fetch Driver
    stmt_d = select(Driver).where(Driver.id == driver_id)
    db_driver = db.execute(stmt_d).scalar_one_or_none()
    if not db_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver does not exist."
        )
        
    # Check if vehicle is AVAILABLE (unless currently assigned to this trip)
    is_same_vehicle = False
    if exclude_trip_id:
        current_trip = trip_repository.get_trip(db, exclude_trip_id)
        if current_trip and current_trip.vehicle_id == vehicle_id:
            is_same_vehicle = True
            
    if not is_same_vehicle:
        if db_vehicle.status == VehicleStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A vehicle already assigned to an active trip (ON_TRIP) cannot be assigned to another trip."
            )
        if db_vehicle.status == VehicleStatus.IN_SHOP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is under maintenance (IN_SHOP) and not available for trip assignment."
            )
        # Check active maintenance record status
        stmt_m = select(MaintenanceLog).where(
            MaintenanceLog.vehicle_id == vehicle_id,
            MaintenanceLog.status == MaintenanceStatus.ACTIVE
        )
        active_m = db.execute(stmt_m).scalars().first()
        if active_m:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicles under ACTIVE maintenance cannot be assigned to a trip."
            )
            
        if db_vehicle.status == VehicleStatus.RETIRED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vehicle is retired and cannot be assigned to trips."
            )
        if db_vehicle.status != VehicleStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle must be AVAILABLE (current status: {db_vehicle.status.value})."
            )
            
    # Check if driver is AVAILABLE (unless currently assigned to this trip)
    is_same_driver = False
    if exclude_trip_id:
        current_trip = trip_repository.get_trip(db, exclude_trip_id)
        if current_trip and current_trip.driver_id == driver_id:
            is_same_driver = True
            
    if not is_same_driver:
        if db_driver.status == DriverStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A driver already assigned to an active trip (ON_TRIP) cannot be assigned to another trip."
            )
        if db_driver.status != DriverStatus.AVAILABLE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Driver must be AVAILABLE (current status: {db_driver.status.value})."
            )
            
    # 3. Check Driver Expiration & Suspension
    if db_driver.license_expiry_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver license has expired."
        )
    if db_driver.status == DriverStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Suspended drivers cannot be assigned to trips."
        )
        
    # 4. Check Cargo Capacity
    if cargo_weight > db_vehicle.maximum_load_capacity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cargo weight of {cargo_weight} exceeds vehicle maximum load capacity of {db_vehicle.maximum_load_capacity}."
        )

def create_trip(db: Session, trip_in: TripCreate) -> Trip:
    """Validate assets and create a trip in DRAFT status."""
    validate_trip_entities(db, trip_in.vehicle_id, trip_in.driver_id, trip_in.cargo_weight)
    return trip_repository.create_trip(db, trip_in)

def get_trip(db: Session, trip_id: uuid.UUID) -> Trip:
    """Retrieve a trip by ID or raise 404."""
    db_trip = trip_repository.get_trip(db, trip_id)
    if not db_trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trip with ID '{trip_id}' not found."
        )
    return db_trip

def get_all_trips(
    db: Session,
    status: TripStatus | None = None,
    page: int = 1,
    limit: int = 10
) -> tuple[list[Trip], int]:
    """List trips with status filtering and pagination."""
    return trip_repository.get_all_trips(db, status, page, limit)

def update_trip(db: Session, trip_id: uuid.UUID, trip_in: TripUpdate) -> Trip:
    """Update a draft trip, validating changes."""
    db_trip = get_trip(db, trip_id)
    
    if db_trip.status != TripStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only trips in DRAFT status can be updated."
        )
        
    # Resolve updated values to validate consistency
    target_vehicle_id = trip_in.vehicle_id if trip_in.vehicle_id is not None else db_trip.vehicle_id
    target_driver_id = trip_in.driver_id if trip_in.driver_id is not None else db_trip.driver_id
    target_cargo_weight = trip_in.cargo_weight if trip_in.cargo_weight is not None else db_trip.cargo_weight
    
    validate_trip_entities(db, target_vehicle_id, target_driver_id, target_cargo_weight, exclude_trip_id=trip_id)
    return trip_repository.update_trip(db, db_trip, trip_in)

def delete_trip(db: Session, trip_id: uuid.UUID) -> None:
    """Delete a trip (only allowed for DRAFT or CANCELLED status)."""
    db_trip = get_trip(db, trip_id)
    if db_trip.status not in [TripStatus.DRAFT, TripStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DRAFT or CANCELLED trips can be deleted."
        )
    trip_repository.delete_trip(db, db_trip)

def dispatch_trip(db: Session, trip_id: uuid.UUID) -> Trip:
    """Dispatch a DRAFT trip. Updates trip, vehicle, and driver statuses to ON_TRIP."""
    db_trip = get_trip(db, trip_id)
    
    if db_trip.status != TripStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only trips in DRAFT status can be dispatched."
        )
        
    # Re-validate asset availability before dispatching
    validate_trip_entities(db, db_trip.vehicle_id, db_trip.driver_id, db_trip.cargo_weight, exclude_trip_id=trip_id)
    
    # 1. Update statuses to ON_TRIP
    db_trip.status = TripStatus.DISPATCHED
    db_trip.vehicle.status = VehicleStatus.ON_TRIP
    db_trip.driver.status = DriverStatus.ON_TRIP
    
    db.commit()
    db.refresh(db_trip)
    return db_trip

def complete_trip(db: Session, trip_id: uuid.UUID, complete_in: TripCompleteInput) -> Trip:
    """Complete a DISPATCHED trip, saving fuel & odometer and releasing vehicle & driver."""
    db_trip = get_trip(db, trip_id)
    
    if db_trip.status != TripStatus.DISPATCHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only trips in DISPATCHED status can be completed."
        )
        
    db_vehicle = db_trip.vehicle
    
    # Validate final odometer
    if complete_in.final_odometer <= db_vehicle.odometer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Final odometer ({complete_in.final_odometer}) must be greater than current vehicle odometer ({db_vehicle.odometer})."
        )
        
    # 1. Save odometer and fuel details
    db_trip.final_odometer = complete_in.final_odometer
    db_trip.fuel_consumed = complete_in.fuel_consumed
    db_trip.status = TripStatus.COMPLETED
    
    # 2. Release vehicle and driver to AVAILABLE
    db_vehicle.odometer = complete_in.final_odometer
    db_vehicle.status = VehicleStatus.AVAILABLE
    db_trip.driver.status = DriverStatus.AVAILABLE
    
    db.commit()
    db.refresh(db_trip)
    return db_trip

def cancel_trip(db: Session, trip_id: uuid.UUID) -> Trip:
    """Cancel a DRAFT or DISPATCHED trip. Releases vehicle and driver if previously DISPATCHED."""
    db_trip = get_trip(db, trip_id)
    
    if db_trip.status not in [TripStatus.DRAFT, TripStatus.DISPATCHED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only DRAFT or DISPATCHED trips can be cancelled."
        )
        
    # If the trip was already dispatched, release vehicle and driver to AVAILABLE
    if db_trip.status == TripStatus.DISPATCHED:
        db_trip.vehicle.status = VehicleStatus.AVAILABLE
        db_trip.driver.status = DriverStatus.AVAILABLE
        
    db_trip.status = TripStatus.CANCELLED
    db.commit()
    db.refresh(db_trip)
    return db_trip
