import uuid
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.models.fuel import FuelLog
from app.models.maintenance import MaintenanceLog
from app.models.expense import Expense
from app.core.enums import ExpenseType
from app.schemas.cost_summary import VehicleCostSummary


def get_vehicle_cost_summary(db: Session, vehicle_id: uuid.UUID) -> VehicleCostSummary:
    """
    Calculate and return the operational cost summary for a vehicle.

    Operational Cost = Total Fuel Cost + Total Maintenance Cost + Total Other Expenses
    """
    # Verify vehicle exists
    stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
    db_vehicle = db.execute(stmt).scalar_one_or_none()
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID '{vehicle_id}' not found."
        )

    # Total Fuel Cost & Total Fuel Consumed
    fuel_stmt = select(
        func.coalesce(func.sum(FuelLog.cost), 0.0).label("total_fuel_cost"),
        func.coalesce(func.sum(FuelLog.liters), 0.0).label("total_fuel_consumed"),
    ).where(FuelLog.vehicle_id == vehicle_id)
    fuel_result = db.execute(fuel_stmt).one()
    total_fuel_cost = float(fuel_result.total_fuel_cost)
    total_fuel_consumed = float(fuel_result.total_fuel_consumed)

    # Total Maintenance Cost
    maintenance_stmt = select(
        func.coalesce(func.sum(MaintenanceLog.cost), 0.0).label("total_maintenance_cost"),
    ).where(MaintenanceLog.vehicle_id == vehicle_id)
    maintenance_result = db.execute(maintenance_stmt).one()
    total_maintenance_cost = float(maintenance_result.total_maintenance_cost)

    # Total Other Expenses (all expense types except FUEL to avoid double-counting)
    other_expense_stmt = select(
        func.coalesce(func.sum(Expense.amount), 0.0).label("total_other_expenses"),
    ).where(
        Expense.vehicle_id == vehicle_id,
        Expense.type != ExpenseType.FUEL,
    )
    other_expense_result = db.execute(other_expense_stmt).one()
    total_other_expenses = float(other_expense_result.total_other_expenses)

    # Total Operational Cost
    total_operational_cost = total_fuel_cost + total_maintenance_cost + total_other_expenses

    return VehicleCostSummary(
        vehicle_id=vehicle_id,
        total_fuel_cost=round(total_fuel_cost, 2),
        total_fuel_consumed=round(total_fuel_consumed, 2),
        total_maintenance_cost=round(total_maintenance_cost, 2),
        total_other_expenses=round(total_other_expenses, 2),
        total_operational_cost=round(total_operational_cost, 2),
    )
