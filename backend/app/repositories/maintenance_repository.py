import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.maintenance import MaintenanceLog
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate
from app.core.enums import MaintenanceStatus

def create_log(db: Session, log_in: MaintenanceCreate) -> MaintenanceLog:
    """Create a new maintenance log record."""
    db_log = MaintenanceLog(
        vehicle_id=log_in.vehicle_id,
        maintenance_type=log_in.maintenance_type,
        description=log_in.description,
        start_date=log_in.start_date,
        cost=log_in.cost,
        status=log_in.status
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_log(db: Session, log_id: uuid.UUID) -> MaintenanceLog | None:
    """Retrieve a maintenance log record by ID."""
    stmt = select(MaintenanceLog).where(MaintenanceLog.id == log_id)
    return db.execute(stmt).scalar_one_or_none()

def get_all_logs(
    db: Session,
    status: MaintenanceStatus | None = None,
    vehicle_id: uuid.UUID | None = None,
    page: int = 1,
    limit: int = 10
) -> tuple[list[MaintenanceLog], int]:
    """Retrieve a paginated list of maintenance logs, optionally filtered by status or vehicle."""
    stmt = select(MaintenanceLog)
    
    if status:
        stmt = stmt.where(MaintenanceLog.status == status)
    if vehicle_id:
        stmt = stmt.where(MaintenanceLog.vehicle_id == vehicle_id)
        
    # Count total matches
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # Sort order: newest records first
    stmt = stmt.order_by(MaintenanceLog.created_at.desc())
    
    # Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    
    items = list(db.execute(stmt).scalars().all())
    return items, total

def update_log(db: Session, db_log: MaintenanceLog, log_in: MaintenanceUpdate) -> MaintenanceLog:
    """Update an existing maintenance log record."""
    update_data = log_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def delete_log(db: Session, db_log: MaintenanceLog) -> None:
    """Delete a maintenance log record."""
    db.delete(db_log)
    db.commit()
