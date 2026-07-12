"""update_trip_model

Revision ID: 42f39b601668
Revises: 6ac532b339da
Create Date: 2026-07-12 15:01:19.419045

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '42f39b601668'
down_revision: Union[str, Sequence[str], None] = '6ac532b339da'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create the new Enum type in database
    tripstatus_enum = postgresql.ENUM('DRAFT', 'DISPATCHED', 'COMPLETED', 'CANCELLED', name='tripstatus_enum')
    tripstatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns
    op.add_column('trips', sa.Column('source', sa.String(length=255), nullable=False))
    op.add_column('trips', sa.Column('destination', sa.String(length=255), nullable=False))
    op.add_column('trips', sa.Column('planned_distance', sa.Float(), nullable=False))
    op.add_column('trips', sa.Column('final_odometer', sa.Float(), nullable=True))
    op.add_column('trips', sa.Column('fuel_consumed', sa.Float(), nullable=True))
    
    op.alter_column('trips', 'cargo_weight',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=False)
               
    # 3. Drop status column and recreate with the new Enum type
    op.drop_index('ix_trips_status', table_name='trips')
    op.drop_column('trips', 'status')
    
    op.add_column('trips', sa.Column('status', sa.Enum('DRAFT', 'DISPATCHED', 'COMPLETED', 'CANCELLED', name='tripstatus_enum'), nullable=False))
    op.create_index(op.f('ix_trips_status'), 'trips', ['status'], unique=False)
    
    # 4. Clean up old columns
    op.drop_column('trips', 'start_location')
    op.drop_column('trips', 'end_time')
    op.drop_column('trips', 'start_time')
    op.drop_column('trips', 'distance')
    op.drop_column('trips', 'end_location')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop new status and columns
    op.drop_index(op.f('ix_trips_status'), table_name='trips')
    op.drop_column('trips', 'status')
    
    # 2. Recreate old status column
    op.add_column('trips', sa.Column('status', postgresql.ENUM('SCHEDULED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED', name='tripstatus'), nullable=False))
    op.create_index('ix_trips_status', 'trips', ['status'], unique=False)

    op.alter_column('trips', 'cargo_weight',
               existing_type=sa.DOUBLE_PRECISION(precision=53),
               nullable=True)
               
    op.drop_column('trips', 'fuel_consumed')
    op.drop_column('trips', 'final_odometer')
    op.drop_column('trips', 'planned_distance')
    op.drop_column('trips', 'destination')
    op.drop_column('trips', 'source')

    # 3. Add back old columns
    op.add_column('trips', sa.Column('end_location', sa.VARCHAR(length=255), autoincrement=False, nullable=False))
    op.add_column('trips', sa.Column('distance', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('trips', sa.Column('start_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('trips', sa.Column('end_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True))
    op.add_column('trips', sa.Column('start_location', sa.VARCHAR(length=255), autoincrement=False, nullable=False))

    # 4. Drop the new Enum type from database
    postgresql.ENUM(name='tripstatus_enum').drop(op.get_bind(), checkfirst=True)
