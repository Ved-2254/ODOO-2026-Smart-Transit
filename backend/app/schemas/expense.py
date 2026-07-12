import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.core.enums import ExpenseType


class ExpenseCreate(BaseModel):
    vehicle_id: uuid.UUID
    expense_type: ExpenseType
    amount: float = Field(..., gt=0, description="Expense amount, must be > 0")
    description: str = Field(..., min_length=1, max_length=255)
    expense_date: datetime


class ExpenseUpdate(BaseModel):
    expense_type: ExpenseType | None = None
    amount: float | None = Field(None, gt=0)
    description: str | None = Field(None, min_length=1, max_length=255)
    expense_date: datetime | None = None


class ExpenseResponse(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    expense_type: ExpenseType = Field(validation_alias="type")
    amount: float
    description: str
    expense_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    page: int
    limit: int
    total: int
