from sqlalchemy.orm import Session
from app.repositories import dashboard_repository
from app.core.enums import VehicleStatus, VehicleType
from app.schemas.dashboard import DashboardResponse

def get_dashboard_data(db: Session, vehicle_type: VehicleType | None = None, status: VehicleStatus | None = None) -> DashboardResponse:
    active_vehicles = dashboard_repository.get_active_vehicles_count(db, vehicle_type, status)
    available_vehicles = dashboard_repository.get_available_vehicles_count(db, vehicle_type, status)
    vehicles_in_shop = dashboard_repository.get_vehicles_in_shop_count(db, vehicle_type, status)
    active_trips = dashboard_repository.get_active_trips_count(db, vehicle_type, status)
    pending_trips = dashboard_repository.get_pending_trips_count(db, vehicle_type, status)
    drivers_on_duty = dashboard_repository.get_drivers_on_duty_count(db, vehicle_type, status)
    
    # Vehicles currently ON_TRIP
    vehicles_on_trip = dashboard_repository.get_vehicles_on_trip_count(db, vehicle_type, status)
    
    if active_vehicles > 0:
        fleet_utilization = round((vehicles_on_trip / active_vehicles) * 100, 2)
    else:
        fleet_utilization = 0.0
        
    return DashboardResponse(
        active_vehicles=active_vehicles,
        available_vehicles=available_vehicles,
        vehicles_in_shop=vehicles_in_shop,
        active_trips=active_trips,
        pending_trips=pending_trips,
        drivers_on_duty=drivers_on_duty,
        fleet_utilization=fleet_utilization
    )
