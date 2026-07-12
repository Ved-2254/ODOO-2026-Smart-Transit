import uuid
from decimal import Decimal
from typing import List
from sqlalchemy import Float, Numeric, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin
from app.core.enums import VehicleStatus, VehicleType

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
    vehicle_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    vehicle_model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        SQLEnum(VehicleType, name="vehicletype_enum"),
        nullable=False,
        index=True
    )
    maximum_load_capacity: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    odometer: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    acquisition_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )
    status: Mapped[VehicleStatus] = mapped_column(
        SQLEnum(VehicleStatus, name="vehiclestatus_enum"),
        nullable=False,
        index=True
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
