import enum
import uuid
from typing import List
from sqlalchemy import CheckConstraint, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin

class VehicleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    IN_MAINTENANCE = "IN_MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"

class VehicleType(str, enum.Enum):
    TRUCK = "TRUCK"
    VAN = "VAN"
    BUS = "BUS"
    CAR = "CAR"
    TRAILER = "TRAILER"

class Vehicle(Base, TimestampMixin):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    registration_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    make: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    model: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )
    year: Mapped[int] = mapped_column(
        Integer(),
        nullable=False
    )
    type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicletype"),
        nullable=False
    )
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus, name="vehiclestatus"),
        nullable=False,
        index=True
    )
    capacity: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    odometer: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("capacity > 0", name="check_vehicle_capacity_positive"),
        CheckConstraint("odometer >= 0", name="check_vehicle_odometer_non_negative"),
    )

    # Relationships
    trips: Mapped[List["Trip"]] = relationship(
        "Trip",
        back_populates="vehicle"
    )
    maintenance_logs: Mapped[List["MaintenanceLog"]] = relationship(
        "MaintenanceLog",
        back_populates="vehicle"
    )
    fuel_logs: Mapped[List["FuelLog"]] = relationship(
        "FuelLog",
        back_populates="vehicle"
    )
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="vehicle"
    )
