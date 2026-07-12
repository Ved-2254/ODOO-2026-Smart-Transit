import uuid
from datetime import date
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate
from app.core.enums import DriverStatus, LicenseCategory

def create_driver(db: Session, driver_in: DriverCreate) -> Driver:
    """Create a new driver record."""
    db_driver = Driver(
        full_name=driver_in.full_name,
        license_number=driver_in.license_number,
        license_category=driver_in.license_category,
        license_expiry_date=driver_in.license_expiry_date,
        contact_number=driver_in.contact_number,
        safety_score=driver_in.safety_score,
        status=driver_in.status
    )
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def get_driver(db: Session, driver_id: uuid.UUID) -> Driver | None:
    """Retrieve a driver by ID."""
    stmt = select(Driver).where(Driver.id == driver_id)
    return db.execute(stmt).scalar_one_or_none()

def get_driver_by_license(db: Session, license_number: str) -> Driver | None:
    """Retrieve a driver by license number."""
    stmt = select(Driver).where(Driver.license_number == license_number)
    return db.execute(stmt).scalar_one_or_none()

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
    """Retrieve a paginated list of drivers with filtering, search, and sorting."""
    stmt = select(Driver)
    
    # 1. Filters
    if status:
        stmt = stmt.where(Driver.status == status)
    if license_category:
        stmt = stmt.where(Driver.license_category == license_category)
    if expired is not None:
        if expired:
            stmt = stmt.where(Driver.license_expiry_date < date.today())
        else:
            stmt = stmt.where(Driver.license_expiry_date >= date.today())
    if safety_score_min is not None:
        stmt = stmt.where(Driver.safety_score >= safety_score_min)
        
    # 2. Search
    if search:
        search_filter = f"%{search}%"
        stmt = stmt.where(
            or_(
                Driver.full_name.ilike(search_filter),
                Driver.license_number.ilike(search_filter),
                Driver.contact_number.ilike(search_filter)
            )
        )
        
    # 3. Count total matches (before pagination)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0
    
    # 4. Sorting
    sort_column = getattr(Driver, sort_by, Driver.created_at)
    if order == "desc":
        stmt = stmt.order_by(sort_column.desc())
    else:
        stmt = stmt.order_by(sort_column.asc())
        
    # 5. Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    
    items = list(db.execute(stmt).scalars().all())
    return items, total

def update_driver(db: Session, db_driver: Driver, driver_in: DriverUpdate) -> Driver:
    """Update an existing driver record."""
    update_data = driver_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_driver, field, value)
    db.add(db_driver)
    db.commit()
    db.refresh(db_driver)
    return db_driver

def delete_driver(db: Session, db_driver: Driver) -> None:
    """Delete a driver record."""
    db.delete(db_driver)
    db.commit()
