# Role-Based Access Control (RBAC) Status - TransitOps Backend

This document details the design, configuration, and verification of the Role-Based Access Control (RBAC) module implemented in the TransitOps FastAPI backend.

---

## 1. Allowed Roles

The database supports the following 5 distinct roles (automatically seeded on application startup):

1. **Admin**: Universal read/write access.
2. **Fleet Manager**: Operational control over vehicles and driver assignments.
3. **Safety Officer**: Compliance and driver status supervision.
4. **Financial Analyst**: Access to expense reports and fuel records.
5. **Driver**: Limited access to assigned tasks and trips (not allowed to view global vehicle listings, other driver records, or expenses).

---

## 2. Protected Endpoints & Authorization Rules

The security rules are enforced at the endpoint level via the reusable `Depends(require_roles(*roles))` dependency.

| HTTP Method | Endpoint | Allowed Roles | Description |
|---|---|---|---|
| `GET` | `/vehicles` | `Admin`, `Fleet Manager` | List all vehicles in the registry. |
| `POST` | `/vehicles` | `Admin`, `Fleet Manager` | Create/register a new vehicle. |
| `GET` | `/drivers` | `Admin`, `Fleet Manager`, `Safety Officer` | List all drivers. |
| `GET` | `/expenses` | `Admin`, `Financial Analyst` | Access financial expense details. |

---

## 3. Reusable Authorization Dependency

The authorization middleware guard is implemented inside `backend/app/core/dependencies.py` as a parameterized dependency factory:

```python
def require_roles(*allowed_roles: str):
    """
    Dependency factory to enforce role-based access control.
    Raises 403 Forbidden if current user's role is not allowed.
    """
    def role_dependency(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.role or current_user.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role not authorized."
            )
        return current_user
    return role_dependency
```

---

## 4. Usage Examples

### A. Protecting a Route
```python
from fastapi import APIRouter, Depends
from app.core.dependencies import require_roles

router = APIRouter()

@router.get("/vehicles")
def get_vehicles(user=Depends(require_roles("Fleet Manager", "Admin"))):
    return {"data": "vehicles list"}
```

### B. Success Example (`200 OK`)
- **Request**: `GET /vehicles`
- **Headers**: `Authorization: Bearer <TOKEN_OF_FLEET_MANAGER_OR_ADMIN>`
- **Response**:
```json
[
  {
    "id": "7a3b4e67-d890-410a-bf12-58e92d6bba78",
    "registration_number": "TX-1234",
    "make": "Volvo",
    "model": "VNL",
    "status": "ACTIVE"
  }
]
```

### C. Failure Example (`403 Forbidden`)
- **Request**: `GET /vehicles`
- **Headers**: `Authorization: Bearer <TOKEN_OF_DRIVER>`
- **Response**:
```json
{
  "detail": "Access denied. User role not authorized."
}
```

---

## 5. Testing Instructions

### Automated Tests
Verify all RBAC combinations using the Pytest integration suite:
```powershell
.\venv\Scripts\python -m pytest app/tests/test_rbac.py -v
```

### Manual Verification
1. Open the API documentation page at `http://localhost:8000/docs`.
2. Retrieve tokens for different roles by registering/logging in users with `Admin`, `Fleet Manager`, `Driver`, etc.
3. Test endpoints with different user roles by clicking **Authorize** and supplying the appropriate JWT token. Observe the return of `200 OK` (success) vs `403 Forbidden` (failure) status codes.
