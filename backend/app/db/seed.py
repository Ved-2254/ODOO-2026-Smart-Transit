import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Role
from app.models.user import User
from app.core.security import hash_password

def seed_roles(db: Session) -> None:
    """Seed standard roles into the database if they do not exist."""
    standard_roles = [
        ("Fleet Manager", "Manages the fleet operations, vehicles, and drivers."),
        ("Dispatcher", "Schedules and dispatches trips to drivers."),
        ("Safety Officer", "Monages safety guidelines and driver compliance."),
        ("Financial Analyst", "Monitors fuel costs, expenses, and revenues."),
        ("Driver", "Operates vehicles and records trip updates."),
        ("Admin", "Full administrative access control.")
    ]
    
    for name, desc in standard_roles:
        stmt = select(Role).where(Role.name == name)
        role = db.execute(stmt).scalar_one_or_none()
        if not role:
            db_role = Role(
                id=uuid.uuid4(),
                name=name,
                description=desc
            )
            db.add(db_role)
    db.commit()

    # Seed default user if it does not exist
    user_stmt = select(User).where(User.email == "admin@transitops.com")
    admin_user = db.execute(user_stmt).scalar_one_or_none()
    if not admin_user:
        fleet_manager_role = db.execute(select(Role).where(Role.name == "Fleet Manager")).scalar_one_or_none()
        if fleet_manager_role:
            db_user = User(
                id=uuid.uuid4(),
                email="admin@transitops.com",
                hashed_password=hash_password("admin123"),
                full_name="Admin",
                is_active=True,
                role_id=fleet_manager_role.id
            )
            db.add(db_user)
            db.commit()

