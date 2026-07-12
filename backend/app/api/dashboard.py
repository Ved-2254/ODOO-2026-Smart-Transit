from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import VehicleStatus, VehicleType
from app.schemas.dashboard import DashboardResponse
from app.services import dashboard_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

# Protect the endpoint using the existing JWT and RBAC middleware.
# Allow access to: Admin, Fleet Manager, Safety Officer, Financial Analyst.
read_guard = Depends(require_roles("Admin", "Fleet Manager", "Safety Officer", "Financial Analyst"))

@router.get("/", response_model=DashboardResponse, status_code=status.HTTP_200_OK)
def get_dashboard(
    vehicle_type: VehicleType | None = Query(None),
    status: VehicleStatus | None = Query(None),
    region: str | None = Query(None), # Skipped backend support as Region is not implemented
    db: Session = Depends(get_db),
    _ = read_guard
):
    """
    Retrieve fleet KPI dashboard statistics with optional filtering.
    Allowed roles: Admin, Fleet Manager, Safety Officer, Financial Analyst.
    """
    return dashboard_service.get_dashboard_data(db, vehicle_type=vehicle_type, status=status)
