import uuid
from datetime import date
from typing import List, Optional
from sqlalchemy import Date, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin
from app.core.enums import DriverStatus, LicenseCategory

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
    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    license_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    license_category: Mapped[LicenseCategory] = mapped_column(
        SQLEnum(LicenseCategory, name="licensecategory_enum"),
        nullable=False
    )
    license_expiry_date: Mapped[date] = mapped_column(
        Date(),
        nullable=False,
        index=True
    )
    contact_number: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )
    safety_score: Mapped[int] = mapped_column(
        Integer(),
        nullable=False
    )
    status: Mapped[DriverStatus] = mapped_column(
        SQLEnum(DriverStatus, name="driverstatus_enum"),
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
