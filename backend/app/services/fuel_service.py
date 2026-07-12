import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories import fuel_repository
from app.schemas.fuel import FuelLogCreate, FuelLogUpdate
from app.models.fuel import FuelLog
from app.models.vehicle import Vehicle
from app.models.trip import Trip


def create_fuel_log(db: Session, fuel_log_in: FuelLogCreate) -> FuelLog:
    """Create a fuel log after validating vehicle, trip, and odometer constraints."""
    # 1. Vehicle must exist
    stmt = select(Vehicle).where(Vehicle.id == fuel_log_in.vehicle_id)
    db_vehicle = db.execute(stmt).scalar_one_or_none()
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle does not exist."
        )

    # 2. Trip must exist if provided
    if fuel_log_in.trip_id:
        stmt_trip = select(Trip).where(Trip.id == fuel_log_in.trip_id)
        db_trip = db.execute(stmt_trip).scalar_one_or_none()
        if not db_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip does not exist."
            )

    # 3. Odometer cannot decrease compared to the vehicle's current odometer
    if fuel_log_in.odometer < db_vehicle.odometer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Odometer reading ({fuel_log_in.odometer}) cannot be less than the vehicle's current odometer ({db_vehicle.odometer})."
        )

    # 4. Create the fuel log
    db_log = fuel_repository.create_fuel_log(db, fuel_log_in)

    # 5. Update the vehicle's odometer if a higher reading is provided
    if fuel_log_in.odometer > db_vehicle.odometer:
        db_vehicle.odometer = fuel_log_in.odometer
        db.commit()

    return db_log


def get_fuel_log(db: Session, fuel_log_id: uuid.UUID) -> FuelLog:
    """Retrieve a fuel log by ID, raising 404 if not found."""
    db_log = fuel_repository.get_fuel_log(db, fuel_log_id)
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fuel log with ID '{fuel_log_id}' not found."
        )
    return db_log


def get_all_fuel_logs(
    db: Session,
    vehicle_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[FuelLog], int]:
    """Retrieve filtered, paginated fuel logs."""
    return fuel_repository.get_all_fuel_logs(
        db, vehicle_id=vehicle_id, date_from=date_from, date_to=date_to,
        page=page, limit=limit
    )


def update_fuel_log(db: Session, fuel_log_id: uuid.UUID, fuel_log_in: FuelLogUpdate) -> FuelLog:
    """Update a fuel log with odometer validation."""
    db_log = get_fuel_log(db, fuel_log_id)

    # Validate odometer if being updated
    if fuel_log_in.odometer is not None:
        db_vehicle = db_log.vehicle
        # Odometer cannot decrease compared to the vehicle's current odometer
        # (unless the current odometer was set by this very log – we check against vehicle)
        if fuel_log_in.odometer < db_vehicle.odometer and fuel_log_in.odometer < db_log.odometer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Odometer reading ({fuel_log_in.odometer}) cannot be less than the vehicle's current odometer ({db_vehicle.odometer})."
            )

        # Update vehicle odometer if higher
        if fuel_log_in.odometer > db_vehicle.odometer:
            db_vehicle.odometer = fuel_log_in.odometer

    # Validate trip if being updated
    if fuel_log_in.trip_id is not None:
        stmt_trip = select(Trip).where(Trip.id == fuel_log_in.trip_id)
        db_trip = db.execute(stmt_trip).scalar_one_or_none()
        if not db_trip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trip does not exist."
            )

    return fuel_repository.update_fuel_log(db, db_log, fuel_log_in)


def delete_fuel_log(db: Session, fuel_log_id: uuid.UUID) -> None:
    """Delete a fuel log."""
    db_log = get_fuel_log(db, fuel_log_id)
    fuel_repository.delete_fuel_log(db, db_log)
