import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.fuel import FuelLog
from app.schemas.fuel import FuelLogCreate, FuelLogUpdate


def create_fuel_log(db: Session, fuel_log_in: FuelLogCreate) -> FuelLog:
    """Create a new fuel log record."""
    db_log = FuelLog(
        vehicle_id=fuel_log_in.vehicle_id,
        trip_id=fuel_log_in.trip_id,
        fuel_date=fuel_log_in.fuel_date,
        liters=fuel_log_in.liters,
        cost=fuel_log_in.cost,
        odometer=fuel_log_in.odometer,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_fuel_log(db: Session, fuel_log_id: uuid.UUID) -> FuelLog | None:
    """Retrieve a fuel log by its ID."""
    stmt = select(FuelLog).where(FuelLog.id == fuel_log_id)
    return db.execute(stmt).scalar_one_or_none()


def get_all_fuel_logs(
    db: Session,
    vehicle_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[FuelLog], int]:
    """Retrieve a paginated list of fuel logs with optional filters."""
    stmt = select(FuelLog)

    # Filters
    if vehicle_id:
        stmt = stmt.where(FuelLog.vehicle_id == vehicle_id)
    if date_from:
        stmt = stmt.where(FuelLog.fuel_date >= date_from)
    if date_to:
        stmt = stmt.where(FuelLog.fuel_date <= date_to)

    # Count total matches
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    # Sort: newest first
    stmt = stmt.order_by(FuelLog.fuel_date.desc())

    # Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    items = list(db.execute(stmt).scalars().all())
    return items, total


def update_fuel_log(db: Session, db_log: FuelLog, fuel_log_in: FuelLogUpdate) -> FuelLog:
    """Update an existing fuel log record."""
    update_data = fuel_log_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_log, field, value)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def delete_fuel_log(db: Session, db_log: FuelLog) -> None:
    """Delete a fuel log record."""
    db.delete(db_log)
    db.commit()
