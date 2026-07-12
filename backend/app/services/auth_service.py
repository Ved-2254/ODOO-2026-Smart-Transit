import uuid
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role
from app.schemas.auth import UserRegister
from app.core.security import hash_password

def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by email, eager loading their role."""
    stmt = select(User).options(joinedload(User.role)).where(User.email == email)
    return db.execute(stmt).scalar_one_or_none()

def get_user_by_id(db: Session, user_id: uuid.UUID | str) -> User | None:
    """Retrieve a user by ID, converting string input if necessary, eager loading their role."""
    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return None
    stmt = select(User).options(joinedload(User.role)).where(User.id == user_id)
    return db.execute(stmt).scalar_one_or_none()

def get_role_by_name(db: Session, name: str) -> Role | None:
    """Retrieve a role by its name."""
    stmt = select(Role).where(Role.name == name)
    return db.execute(stmt).scalar_one_or_none()

def create_user(db: Session, user_in: UserRegister, role_id: uuid.UUID) -> User:
    """Create a new user with hashed password and role association."""
    db_user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.name,
        role_id=role_id,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    # Refresh to ensure relationships/attributes are fully loaded
    stmt = select(User).options(joinedload(User.role)).where(User.id == db_user.id)
    return db.execute(stmt).scalar_one()
