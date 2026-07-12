import uuid
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories import maintenance_repository
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from app.models.maintenance import MaintenanceLog
from app.models.vehicle import Vehicle
from app.core.enums import MaintenanceStatus, VehicleStatus

def create_maintenance_log(db: Session, log_in: MaintenanceCreate) -> MaintenanceLog:
    """Create a maintenance log and update the vehicle status if active."""
    # 1. Fetch Vehicle
    stmt = select(Vehicle).where(Vehicle.id == log_in.vehicle_id)
    db_vehicle = db.execute(stmt).scalar_one_or_none()
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle does not exist."
        )
        
    if db_vehicle.status == VehicleStatus.RETIRED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Retired vehicles cannot undergo maintenance."
        )
        
    # 2. A vehicle cannot have more than one ACTIVE maintenance record
    if log_in.status == MaintenanceStatus.ACTIVE:
        stmt_active = select(MaintenanceLog).where(
            MaintenanceLog.vehicle_id == log_in.vehicle_id,
            MaintenanceLog.status == MaintenanceStatus.ACTIVE
        )
        existing_active = db.execute(stmt_active).scalars().first()
        if existing_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A vehicle cannot have more than one ACTIVE maintenance record."
            )
            
        # Creating an ACTIVE maintenance record must automatically change vehicle status to IN_SHOP
        db_vehicle.status = VehicleStatus.IN_SHOP
        
    db_log = maintenance_repository.create_log(db, log_in)
    return db_log

def get_maintenance_log(db: Session, log_id: uuid.UUID) -> MaintenanceLog:
    """Retrieve a maintenance log by ID, raising 404 if not found."""
    db_log = maintenance_repository.get_log(db, log_id)
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Maintenance record with ID '{log_id}' not found."
        )
    return db_log

def get_all_logs(
    db: Session,
    status: MaintenanceStatus | None = None,
    vehicle_id: uuid.UUID | None = None,
    page: int = 1,
    limit: int = 10
) -> tuple[list[MaintenanceLog], int]:
    """Retrieve filtered, paginated maintenance logs."""
    return maintenance_repository.get_all_logs(db, status, vehicle_id, page, limit)

def update_maintenance_log(db: Session, log_id: uuid.UUID, log_in: MaintenanceUpdate) -> MaintenanceLog:
    """Update a maintenance log."""
    db_log = get_maintenance_log(db, log_id)
    db_vehicle = db_log.vehicle
    
    old_status = db_log.status
    new_status = log_in.status if log_in.status is not None else old_status
    
    if old_status != new_status:
        # If closing (transitioning ACTIVE -> COMPLETED)
        if new_status == MaintenanceStatus.COMPLETED:
            db_log.end_date = date.today()
            if db_vehicle.status != VehicleStatus.RETIRED:
                db_vehicle.status = VehicleStatus.AVAILABLE
                
        # If re-opening (transitioning COMPLETED -> ACTIVE)
        elif new_status == MaintenanceStatus.ACTIVE:
            # Check active constraint
            stmt_active = select(MaintenanceLog).where(
                MaintenanceLog.vehicle_id == db_log.vehicle_id,
                MaintenanceLog.status == MaintenanceStatus.ACTIVE,
                MaintenanceLog.id != log_id
            )
            existing_active = db.execute(stmt_active).scalars().first()
            if existing_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A vehicle cannot have more than one ACTIVE maintenance record."
                )
                
            db_log.end_date = None
            if db_vehicle.status != VehicleStatus.RETIRED:
                db_vehicle.status = VehicleStatus.IN_SHOP
                
    return maintenance_repository.update_log(db, db_log, log_in)

def close_maintenance_log(db: Session, log_id: uuid.UUID) -> MaintenanceLog:
    """Close a maintenance record, marking it COMPLETED, setting end_date, and releasing vehicle."""
    db_log = get_maintenance_log(db, log_id)
    
    if db_log.status == MaintenanceStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maintenance record is already closed."
        )
        
    db_log.status = MaintenanceStatus.COMPLETED
    db_log.end_date = date.today()
    
    db_vehicle = db_log.vehicle
    if db_vehicle.status != VehicleStatus.RETIRED:
        db_vehicle.status = VehicleStatus.AVAILABLE
        
    db.commit()
    db.refresh(db_log)
    return db_log

def delete_maintenance_log(db: Session, log_id: uuid.UUID) -> None:
    """Delete a maintenance log, releasing vehicle if the log was ACTIVE."""
    db_log = get_maintenance_log(db, log_id)
    
    # If we are deleting an ACTIVE maintenance log, release the vehicle
    if db_log.status == MaintenanceStatus.ACTIVE:
        db_vehicle = db_log.vehicle
        if db_vehicle.status != VehicleStatus.RETIRED:
            db_vehicle.status = VehicleStatus.AVAILABLE
            
    maintenance_repository.delete_log(db, db_log)
