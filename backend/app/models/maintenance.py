import uuid
from datetime import date
from sqlalchemy import CheckConstraint, Date, Enum as SQLEnum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base, TimestampMixin
from app.core.enums import MaintenanceStatus

class MaintenanceLog(Base, TimestampMixin):
    __tablename__ = "maintenance_logs"

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
    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )
    start_date: Mapped[date] = mapped_column(
        Date(),
        nullable=False
    )
    end_date: Mapped[date | None] = mapped_column(
        Date(),
        nullable=True
    )
    cost: Mapped[float] = mapped_column(
        Float(),
        nullable=False
    )
    status: Mapped[MaintenanceStatus] = mapped_column(
        SQLEnum(MaintenanceStatus, name="maintenancestatus_enum"),
        nullable=False,
        index=True
    )

    __table_args__ = (
        CheckConstraint("cost >= 0", name="check_maintenance_cost_non_negative"),
    )

    # Relationships
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle",
        back_populates="maintenance_logs"
    )
