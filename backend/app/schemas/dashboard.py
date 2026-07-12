from pydantic import BaseModel, Field

class DashboardResponse(BaseModel):
    active_vehicles: int = Field(..., description="Count of vehicles not in RETIRED status")
    available_vehicles: int = Field(..., description="Count of vehicles in AVAILABLE status")
    vehicles_in_shop: int = Field(..., description="Count of vehicles in IN_SHOP status")
    active_trips: int = Field(..., description="Count of trips in DISPATCHED status")
    pending_trips: int = Field(..., description="Count of trips in DRAFT status")
    drivers_on_duty: int = Field(..., description="Count of drivers in AVAILABLE or ON_TRIP status")
    fleet_utilization: float = Field(..., description="Percentage of active vehicles currently on a trip")
