import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import require_roles
from app.core.enums import ExpenseType
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseListResponse
from app.services import expense_service

router = APIRouter(prefix="/api/v1/expenses", tags=["expenses"])

# Access control guards
write_guard = Depends(require_roles("Fleet Manager", "Admin", "Financial Analyst"))
read_guard = Depends(require_roles("Fleet Manager", "Admin", "Financial Analyst", "Safety Officer"))


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Create a new expense. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    return expense_service.create_expense(db, expense_in)


@router.get("/", response_model=ExpenseListResponse)
def list_expenses(
    vehicle_id: uuid.UUID | None = Query(None),
    expense_type: ExpenseType | None = Query(None),
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _ = read_guard
):
    """List expenses with optional filters. Allowed roles: Fleet Manager, Admin, Financial Analyst, Safety Officer."""
    items, total = expense_service.get_all_expenses(
        db, vehicle_id=vehicle_id, expense_type=expense_type,
        date_from=date_from, date_to=date_to,
        page=page, limit=limit
    )
    return ExpenseListResponse(items=items, page=page, limit=limit, total=total)


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = read_guard
):
    """Retrieve an expense by ID. Allowed roles: Fleet Manager, Admin, Financial Analyst, Safety Officer."""
    return expense_service.get_expense(db, expense_id)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: uuid.UUID,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Update an expense. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    return expense_service.update_expense(db, expense_id, expense_in)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: uuid.UUID,
    db: Session = Depends(get_db),
    _ = write_guard
):
    """Delete an expense. Allowed roles: Fleet Manager, Admin, Financial Analyst."""
    expense_service.delete_expense(db, expense_id)
