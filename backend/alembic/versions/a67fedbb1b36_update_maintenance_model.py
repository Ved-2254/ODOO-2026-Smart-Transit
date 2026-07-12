"""update_maintenance_model

Revision ID: a67fedbb1b36
Revises: 42f39b601668
Create Date: 2026-07-12 15:22:15.353108

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a67fedbb1b36'
down_revision: Union[str, Sequence[str], None] = '42f39b601668'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the new Enum type in database
    maintenancestatus_enum = postgresql.ENUM('ACTIVE', 'COMPLETED', name='maintenancestatus_enum')
    maintenancestatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add new columns
    op.add_column('maintenance_logs', sa.Column('maintenance_type', sa.String(length=100), nullable=False))
    op.add_column('maintenance_logs', sa.Column('start_date', sa.Date(), nullable=False))
    op.add_column('maintenance_logs', sa.Column('end_date', sa.Date(), nullable=True))
    
    # 3. Drop old status column and recreate with the new Enum type
    op.drop_column('maintenance_logs', 'status')
    op.add_column('maintenance_logs', sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', name='maintenancestatus_enum'), nullable=False))
    op.create_index(op.f('ix_maintenance_logs_status'), 'maintenance_logs', ['status'], unique=False)
    
    # 4. Clean up old columns
    op.drop_column('maintenance_logs', 'performed_at')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop new status and columns
    op.drop_index(op.f('ix_maintenance_logs_status'), table_name='maintenance_logs')
    op.drop_column('maintenance_logs', 'status')
    
    # 2. Recreate old status column
    op.add_column('maintenance_logs', sa.Column('status', postgresql.ENUM('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='maintenancestatus'), nullable=False))
    
    op.drop_column('maintenance_logs', 'end_date')
    op.drop_column('maintenance_logs', 'start_date')
    op.drop_column('maintenance_logs', 'maintenance_type')
    
    # 3. Add back old columns
    op.add_column('maintenance_logs', sa.Column('performed_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))

    # 4. Drop the new Enum type from database
    postgresql.ENUM(name='maintenancestatus_enum').drop(op.get_bind(), checkfirst=True)
