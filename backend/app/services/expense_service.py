import uuid
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.repositories import expense_repository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.models.expense import Expense
from app.models.vehicle import Vehicle
from app.core.enums import ExpenseType


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """Create an expense after validating vehicle existence."""
    # Vehicle must exist
    stmt = select(Vehicle).where(Vehicle.id == expense_in.vehicle_id)
    db_vehicle = db.execute(stmt).scalar_one_or_none()
    if not db_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle does not exist."
        )

    return expense_repository.create_expense(db, expense_in)


def get_expense(db: Session, expense_id: uuid.UUID) -> Expense:
    """Retrieve an expense by ID, raising 404 if not found."""
    db_expense = expense_repository.get_expense(db, expense_id)
    if not db_expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Expense with ID '{expense_id}' not found."
        )
    return db_expense


def get_all_expenses(
    db: Session,
    vehicle_id: uuid.UUID | None = None,
    expense_type: ExpenseType | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Expense], int]:
    """Retrieve filtered, paginated expenses."""
    return expense_repository.get_all_expenses(
        db, vehicle_id=vehicle_id, expense_type=expense_type,
        date_from=date_from, date_to=date_to,
        page=page, limit=limit
    )


def update_expense(db: Session, expense_id: uuid.UUID, expense_in: ExpenseUpdate) -> Expense:
    """Update an expense."""
    db_expense = get_expense(db, expense_id)
    return expense_repository.update_expense(db, db_expense, expense_in)


def delete_expense(db: Session, expense_id: uuid.UUID) -> None:
    """Delete an expense."""
    db_expense = get_expense(db, expense_id)
    expense_repository.delete_expense(db, db_expense)
