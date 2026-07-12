import enum
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import CheckConstraint, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin

class TripStatus(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    IN_TRANSIT = "IN_TRANSIT"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False
    )
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[TripStatus] = mapped_column(
        Enum(TripStatus, name="tripstatus"),
        nullable=False,
        index=True
    )
    start_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    end_location: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    cargo_weight: Mapped[Optional[float]] = mapped_column(
        Float(),
        nullable=True
    )
    distance: Mapped[Optional[float]] = mapped_column(
        Float(),
        nullable=True
    )

    __table_args__ = (
        CheckConstraint("cargo_weight >= 0", name="check_trip_cargo_weight_non_negative"),
        CheckConstraint("distance >= 0", name="check_trip_distance_non_negative"),
    )

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="trips"
    )
    driver: Mapped["Driver"] = relationship(
        "Driver",
        back_populates="trips"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="trip"
    )
