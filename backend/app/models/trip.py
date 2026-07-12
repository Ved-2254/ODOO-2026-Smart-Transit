import uuid
from typing import List
from sqlalchemy import CheckConstraint, Enum as SQLEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin
from app.core.enums import TripStatus

class Trip(Base, TimestampMixin):
    __tablename__ = "trips"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    destination: Mapped[str] = mapped_column(
        String(255),
        nullable=False
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
    cargo_weight: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    planned_distance: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    final_odometer: Mapped[float | None] = mapped_column(
        Float(),
        nullable=True
    )
    fuel_consumed: Mapped[float | None] = mapped_column(
        Float(),
        nullable=True
    )
    status: Mapped[TripStatus] = mapped_column(
        SQLEnum(TripStatus, name="tripstatus_enum"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("cargo_weight >= 0", name="check_trip_cargo_weight_non_negative"),
        CheckConstraint("planned_distance >= 0", name="check_trip_distance_non_negative"),
        CheckConstraint("final_odometer >= 0", name="check_trip_final_odometer_non_negative"),
        CheckConstraint("fuel_consumed >= 0", name="check_trip_fuel_consumed_non_negative"),
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
    fuel_logs: Mapped[List["FuelLog"]] = relationship(
        "FuelLog",
        back_populates="trip"
    )
