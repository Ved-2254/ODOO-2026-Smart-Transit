from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import UserRegister, UserResponse, UserLogin, TokenResponse
from app.services import auth_service
from app.core.security import verify_password, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    Validates email uniqueness, password complexity, and role existence.
    """
    # 1. Validation: check unique email
    existing_user = auth_service.get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2. Validation: role must exist
    role = auth_service.get_role_by_name(db, name=user_in.role)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{user_in.role}' does not exist"
        )
    
    # 3. Create user and return
    user = auth_service.create_user(db, user_in=user_in, role_id=role.id)
    return UserResponse(
        id=user.id,
        name=user.full_name,
        email=user.email,
        role=user.role.name if user.role else ""
    )

@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Login endpoint to authenticate credentials and issue access token.
    """
    # 1. Retrieve user
    user = auth_service.get_user_by_email(db, email=login_in.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 2. Verify credentials
    if not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # 3. Check status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive"
        )
    
    # 4. Generate token payload and JWT
    token_payload = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role.name if user.role else ""
    }
    access_token = create_access_token(data=token_payload)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            name=user.full_name,
            email=user.email,
            role=user.role.name if user.role else ""
        )
    )

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Retrieve details of the currently authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.name if current_user.role else ""
    )
