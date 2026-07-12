"""update_vehicle_model

Revision ID: 8fa0f51a9543
Revises: e8d69933f700
Create Date: 2026-07-12 14:24:52.311022

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8fa0f51a9543'
down_revision: Union[str, Sequence[str], None] = 'e8d69933f700'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create new enum types in the database
    vehicletype_enum = postgresql.ENUM('Truck', 'Van', 'Pickup', 'Mini_Truck', 'Bus', 'Other', name='vehicletype_enum')
    vehicletype_enum.create(op.get_bind(), checkfirst=True)

    vehiclestatus_enum = postgresql.ENUM('AVAILABLE', 'ON_TRIP', 'IN_SHOP', 'RETIRED', name='vehiclestatus_enum')
    vehiclestatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add new columns
    op.add_column('vehicles', sa.Column('vehicle_name', sa.String(length=100), nullable=False))
    op.add_column('vehicles', sa.Column('vehicle_model', sa.String(length=100), nullable=False))
    op.add_column('vehicles', sa.Column('vehicle_type', sa.Enum('Truck', 'Van', 'Pickup', 'Mini_Truck', 'Bus', 'Other', name='vehicletype_enum'), nullable=False))
    op.add_column('vehicles', sa.Column('maximum_load_capacity', sa.Float(), nullable=False))
    op.add_column('vehicles', sa.Column('acquisition_cost', sa.Numeric(precision=12, scale=2), nullable=False))
    
    # Drop old status column and index
    op.drop_index('ix_vehicles_status', table_name='vehicles')
    op.drop_column('vehicles', 'status')
    
    # Recreate status column with new enum
    op.add_column('vehicles', sa.Column('status', sa.Enum('AVAILABLE', 'ON_TRIP', 'IN_SHOP', 'RETIRED', name='vehiclestatus_enum'), nullable=False))
    
    # Create indexes
    op.create_index(op.f('ix_vehicles_vehicle_type'), 'vehicles', ['vehicle_type'], unique=False)
    op.create_index(op.f('ix_vehicles_status'), 'vehicles', ['status'], unique=False)
    
    # Drop old columns
    op.drop_column('vehicles', 'year')
    op.drop_column('vehicles', 'capacity')
    op.drop_column('vehicles', 'make')
    op.drop_column('vehicles', 'type')
    op.drop_column('vehicles', 'model')


def downgrade() -> None:
    """Downgrade schema."""
    # Drop new indexes and columns
    op.drop_index(op.f('ix_vehicles_status'), table_name='vehicles')
    op.drop_index(op.f('ix_vehicles_vehicle_type'), table_name='vehicles')
    op.drop_column('vehicles', 'status')
    
    # Recreate old status column and index
    op.add_column('vehicles', sa.Column('status', postgresql.ENUM('ACTIVE', 'IN_MAINTENANCE', 'OUT_OF_SERVICE', name='vehiclestatus'), nullable=False))
    op.create_index('ix_vehicles_status', 'vehicles', ['status'], unique=False)

    op.drop_column('vehicles', 'acquisition_cost')
    op.drop_column('vehicles', 'maximum_load_capacity')
    op.drop_column('vehicles', 'vehicle_type')
    op.drop_column('vehicles', 'vehicle_model')
    op.drop_column('vehicles', 'vehicle_name')

    # Add old columns back
    op.add_column('vehicles', sa.Column('model', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('vehicles', sa.Column('type', postgresql.ENUM('TRUCK', 'VAN', 'BUS', 'CAR', 'TRAILER', name='vehicletype'), autoincrement=False, nullable=False))
    op.add_column('vehicles', sa.Column('make', sa.VARCHAR(length=50), autoincrement=False, nullable=False))
    op.add_column('vehicles', sa.Column('capacity', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=False))
    op.add_column('vehicles', sa.Column('year', sa.INTEGER(), autoincrement=False, nullable=False))

    # Drop new enum types from the database
    postgresql.ENUM(name='vehicletype_enum').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='vehiclestatus_enum').drop(op.get_bind(), checkfirst=True)
