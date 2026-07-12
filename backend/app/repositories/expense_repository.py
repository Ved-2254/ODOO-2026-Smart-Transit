import uuid
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.core.enums import ExpenseType


def create_expense(db: Session, expense_in: ExpenseCreate) -> Expense:
    """Create a new expense record."""
    db_expense = Expense(
        vehicle_id=expense_in.vehicle_id,
        type=expense_in.expense_type,
        amount=expense_in.amount,
        description=expense_in.description,
        expense_date=expense_in.expense_date,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expense(db: Session, expense_id: uuid.UUID) -> Expense | None:
    """Retrieve an expense by its ID."""
    stmt = select(Expense).where(Expense.id == expense_id)
    return db.execute(stmt).scalar_one_or_none()


def get_all_expenses(
    db: Session,
    vehicle_id: uuid.UUID | None = None,
    expense_type: ExpenseType | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[Expense], int]:
    """Retrieve a paginated list of expenses with optional filters."""
    stmt = select(Expense)

    # Filters
    if vehicle_id:
        stmt = stmt.where(Expense.vehicle_id == vehicle_id)
    if expense_type:
        stmt = stmt.where(Expense.type == expense_type)
    if date_from:
        stmt = stmt.where(Expense.expense_date >= date_from)
    if date_to:
        stmt = stmt.where(Expense.expense_date <= date_to)

    # Count total matches
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    # Sort: newest first
    stmt = stmt.order_by(Expense.expense_date.desc())

    # Pagination
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)

    items = list(db.execute(stmt).scalars().all())
    return items, total


def update_expense(db: Session, db_expense: Expense, expense_in: ExpenseUpdate) -> Expense:
    """Update an existing expense record."""
    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Map schema field 'expense_type' to model column 'type'
        if field == "expense_type":
            setattr(db_expense, "type", value)
        else:
            setattr(db_expense, field, value)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, db_expense: Expense) -> None:
    """Delete an expense record."""
    db.delete(db_expense)
    db.commit()
