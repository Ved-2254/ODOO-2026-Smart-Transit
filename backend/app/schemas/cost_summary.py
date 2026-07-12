import uuid
from pydantic import BaseModel


class VehicleCostSummary(BaseModel):
    vehicle_id: uuid.UUID
    total_fuel_cost: float
    total_fuel_consumed: float
    total_maintenance_cost: float
    total_other_expenses: float
    total_operational_cost: float
