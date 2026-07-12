import uuid
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.models.trip import Trip
from app.models.driver import Driver
from app.core.enums import VehicleStatus, VehicleType, TripStatus, DriverStatus

def get_active_vehicles_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    stmt = select(func.count(Vehicle.id)).where(Vehicle.status != VehicleStatus.RETIRED)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    if status:
        stmt = stmt.where(Vehicle.status == status)
    return db.execute(stmt).scalar() or 0

def get_available_vehicles_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    if status and status != VehicleStatus.AVAILABLE:
        return 0
    stmt = select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.AVAILABLE)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    return db.execute(stmt).scalar() or 0

def get_vehicles_in_shop_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    if status and status != VehicleStatus.IN_SHOP:
        return 0
    stmt = select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.IN_SHOP)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    return db.execute(stmt).scalar() or 0

def get_active_trips_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    stmt = select(func.count(Trip.id)).join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Trip.status == TripStatus.DISPATCHED)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    if status:
        stmt = stmt.where(Vehicle.status == status)
    return db.execute(stmt).scalar() or 0

def get_pending_trips_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    stmt = select(func.count(Trip.id)).join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Trip.status == TripStatus.DRAFT)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    if status:
        stmt = stmt.where(Vehicle.status == status)
    return db.execute(stmt).scalar() or 0

def get_drivers_on_duty_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    if vehicle_type or status:
        stmt = (
            select(func.count(Driver.id))
            .join(Trip, Driver.id == Trip.driver_id)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(Driver.status == DriverStatus.ON_TRIP)
            .where(Trip.status == TripStatus.DISPATCHED)
        )
        if vehicle_type:
            stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
        if status:
            stmt = stmt.where(Vehicle.status == status)
    else:
        stmt = select(func.count(Driver.id)).where(
            Driver.status.in_([DriverStatus.AVAILABLE, DriverStatus.ON_TRIP])
        )
    return db.execute(stmt).scalar() or 0

def get_vehicles_on_trip_count(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> int:
    if status and status != VehicleStatus.ON_TRIP:
        return 0
    stmt = select(func.count(Vehicle.id)).where(Vehicle.status == VehicleStatus.ON_TRIP)
    if vehicle_type:
        stmt = stmt.where(Vehicle.vehicle_type == vehicle_type)
    return db.execute(stmt).scalar() or 0
