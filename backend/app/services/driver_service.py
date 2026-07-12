import uuid
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories import driver_repository
from app.schemas.driver import DriverCreate, DriverUpdate
from app.core.enums import DriverStatus, LicenseCategory
from app.models.driver import Driver

def create_driver(db: Session, driver_in: DriverCreate) -> Driver:
    """Validate uniqueness and expiration date, then create driver record."""
    # 1. Unique License Number
    existing = driver_repository.get_driver_by_license(db, driver_in.license_number)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate license number. A driver with this license number already exists."
        )
        
    # 2. Reject Expired License
    if driver_in.license_expiry_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="License has expired. Cannot register a driver with an expired license."
        )
        
    # 3. Reject marking expired licenses as AVAILABLE
    if driver_in.status == DriverStatus.AVAILABLE and driver_in.license_expiry_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drivers with expired licenses cannot be marked AVAILABLE."
        )
        
    return driver_repository.create_driver(db, driver_in)

def get_driver(db: Session, driver_id: uuid.UUID) -> Driver:
    """Retrieve a driver by ID, raising 404 if not found."""
    driver = driver_repository.get_driver(db, driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with ID '{driver_id}' not found."
        )
    return driver

def get_all_drivers(
    db: Session,
    status: DriverStatus | None = None,
    license_category: LicenseCategory | None = None,
    expired: bool | None = None,
    safety_score_min: int | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    order: str = "asc"
) -> tuple[list[Driver], int]:
    """Retrieve filtered, searched, paginated, and sorted list of drivers."""
    return driver_repository.get_all_drivers(
        db, status, license_category, expired, safety_score_min, search, page, limit, sort_by, order
    )

def update_driver(db: Session, driver_id: uuid.UUID, driver_in: DriverUpdate) -> Driver:
    """Update a driver record, checking license uniqueness and status constraints."""
    db_driver = get_driver(db, driver_id)
    
    # 1. Unique License Number
    if driver_in.license_number:
        existing = driver_repository.get_driver_by_license(db, driver_in.license_number)
        if existing and existing.id != driver_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate license number. This license number is already in use by another driver."
            )
            
    # Resolve state variables
    new_expiry = driver_in.license_expiry_date if driver_in.license_expiry_date is not None else db_driver.license_expiry_date
    new_status = driver_in.status if driver_in.status is not None else db_driver.status
    
    # 2. Drivers with expired licenses cannot be marked AVAILABLE
    if new_status == DriverStatus.AVAILABLE and new_expiry < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Drivers with expired licenses cannot be marked AVAILABLE."
        )
        
    # 3. Trip assignment validation rules (when changing status to ON_TRIP)
    if driver_in.status == DriverStatus.ON_TRIP:
        if db_driver.status == DriverStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Suspended drivers cannot be assigned to trips."
            )
        if new_expiry < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Drivers with expired licenses cannot be assigned to trips."
            )
        if db_driver.status == DriverStatus.ON_TRIP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Drivers whose status is ON_TRIP cannot be assigned to another trip."
            )
            
    return driver_repository.update_driver(db, db_driver, driver_in)

def delete_driver(db: Session, driver_id: uuid.UUID) -> None:
    """Delete a driver record, preventing deletion if currently ON_TRIP."""
    db_driver = get_driver(db, driver_id)
    
    if db_driver.status == DriverStatus.ON_TRIP:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete driver because status is ON_TRIP."
        )
        
    driver_repository.delete_driver(db, db_driver)
