import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.role import Role

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
