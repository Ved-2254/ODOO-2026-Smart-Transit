from fastapi import APIRouter, Depends, status
from app.core.dependencies import require_roles

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.get("", status_code=status.HTTP_200_OK)
def list_expenses(current_user=Depends(require_roles("Financial Analyst", "Admin"))):
    """
    Retrieve expenses list. Allowed roles: Financial Analyst, Admin.
    """
    return [
        {
            "id": "9a8b7c6d-5e4f-3a2b-1c0d-9e8f7a6b5c4d",
            "amount": 120.50,
            "type": "FUEL",
            "description": "Weekly fuel refill"
        }
    ]
