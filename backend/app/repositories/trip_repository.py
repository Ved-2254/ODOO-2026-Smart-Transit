import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate
from app.core.enums import TripStatus

def create_trip(db: Session, trip_in: TripCreate) -> Trip:
    """Create a new trip in DRAFT status."""
    db_trip = Trip(
        source=trip_in.source,
        destination=trip_in.destination,
        vehicle_id=trip_in.vehicle_id,
        driver_id=trip_in.driver_id,
        cargo_weight=trip_in.cargo_weight,
        planned_distance=trip_in.planned_distance,
        status=TripStatus.DRAFT
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def get_trip(db: Session, trip_id: uuid.UUID) -> Trip | None:
    """Retrieve a trip by ID."""
    stmt = select(Trip).where(Trip.id == trip_id)
    return db.execute(stmt).scalar_one_or_none()

def get_all_trips(
    db: Session,
    status: TripStatus | None = None,
    page: int = 1,
    limit: int = 10
) -> tuple[list[Trip], int]:
    """Retrieve a paginated list of trips, filtered by status."""
    stmt = select(Trip)
    
    if status:
        stmt = stmt.where(Trip.status == status)
        
    # Count total matches
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # Sorting: order by created_at desc to show newest trips first
    stmt = stmt.order_by(Trip.created_at.desc())
    
    # Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    
    items = list(db.execute(stmt).scalars().all())
    return items, total

def update_trip(db: Session, db_trip: Trip, trip_in: TripUpdate) -> Trip:
    """Update a trip's fields."""
    update_data = trip_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_trip, field, value)
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return db_trip

def delete_trip(db: Session, db_trip: Trip) -> None:
    """Delete a trip record."""
    db.delete(db_trip)
    db.commit()
