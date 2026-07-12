from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.security import decode_access_token
from app.services import auth_service
from app.models.user import User

# Setting auto_error=False allows us to return a proper 401 Unauthorized
# instead of a default 403 Forbidden for missing authorization headers.
reusable_oauth2 = HTTPBearer(auto_error=False)

def get_current_user(
    token: HTTPAuthorizationCredentials | None = Depends(reusable_oauth2),
    db: Session = Depends(get_db)
) -> User:
    """
    Validate access token and return the current user.
    Raises 401 Unauthorized on authentication failures.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = auth_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or has been deleted",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

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

