import uuid
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.core.enums import VehicleStatus, VehicleType

def create_vehicle(db: Session, vehicle_in: VehicleCreate) -> Vehicle:
    """Create a new vehicle record."""
    db_vehicle = Vehicle(
        registration_number=vehicle_in.registration_number,
        vehicle_name=vehicle_in.vehicle_name,
        vehicle_model=vehicle_in.vehicle_model,
        vehicle_type=vehicle_in.vehicle_type,
        maximum_load_capacity=vehicle_in.maximum_load_capacity,
        odometer=vehicle_in.odometer,
        acquisition_cost=vehicle_in.acquisition_cost,
        status=vehicle_in.status
    )
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_vehicle(db: Session, vehicle_id: uuid.UUID) -> Vehicle | None:
    """Retrieve a vehicle by its ID."""
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
    return db.execute(stmt).scalar_one_or_none()

def get_vehicle_by_registration(db: Session, registration_number: str) -> Vehicle | None:
    """Retrieve a vehicle by its registration number."""
    stmt = select(Vehicle).where(Vehicle.registration_number == registration_number)
    return db.execute(stmt).scalar_one_or_none()

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
    """Retrieve a paginated list of vehicles based on filter, search, and sort criteria."""
    stmt = select(Vehicle)
    
    # 1. Filters
    if status:
        stmt = stmt.where(Vehicle.status == status)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
        
    # 2. Search
    if search:
        search_filter = f"%{search}%"
        stmt = stmt.where(
            or_(
                Vehicle.registration_number.ilike(search_filter),
                Vehicle.vehicle_name.ilike(search_filter),
                Vehicle.vehicle_model.ilike(search_filter)
            )
        )
        
    # 3. Total Count (before pagination)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 4. Sorting
    sort_column = getattr(Vehicle, sort_by, Vehicle.created_at)
    if order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())
        
    # 5. Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    
    items = list(db.execute(stmt).scalars().all())
    return items, total

def update_vehicle(db: Session, db_vehicle: Vehicle, vehicle_in: VehicleUpdate) -> Vehicle:
    """Update an existing vehicle record."""
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vehicle, field, value)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def delete_vehicle(db: Session, db_vehicle: Vehicle) -> None:
    """Delete a vehicle record."""
    db.delete(db_vehicle)
    db.commit()
