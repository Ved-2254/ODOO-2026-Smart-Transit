import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin

class FuelLog(Base, TimestampMixin):
    __tablename__ = "fuel_logs"

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
    driver_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True
    )
    fuel_quantity: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    price_per_unit: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    odometer_at_fill: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    fill_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("fuel_quantity >= 0", name="check_fuel_quantity_non_negative"),
        CheckConstraint("price_per_unit >= 0", name="check_fuel_price_non_negative"),
        CheckConstraint("odometer_at_fill >= 0", name="check_fuel_odometer_non_negative"),
    )

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="fuel_logs"
    )
    driver: Mapped[Optional["Driver"]] = relationship(
        "Driver",
        back_populates="fuel_logs"
    )
