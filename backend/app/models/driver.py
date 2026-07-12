import enum
import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin

class DriverStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ON_TRIP = "ON_TRIP"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"

class Driver(Base, TimestampMixin):
    __tablename__ = "drivers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        nullable=True
    )
    license_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )
    license_expiry: Mapped[date] = mapped_column(
        Date(),
        nullable=False,
        index=True
    )
    status: Mapped[DriverStatus] = mapped_column(
        Enum(DriverStatus, name="driverstatus"),
        nullable=False,
        index=True
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="driver_profile"
    )
    trips: Mapped[List["Trip"]] = relationship(
        "Trip",
        back_populates="driver"
    )
    fuel_logs: Mapped[List["FuelLog"]] = relationship(
        "FuelLog",
        back_populates="driver"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="driver"
    )
