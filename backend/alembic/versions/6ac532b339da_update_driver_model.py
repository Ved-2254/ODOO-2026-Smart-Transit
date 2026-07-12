"""update_driver_model

Revision ID: 6ac532b339da
Revises: 8fa0f51a9543
Create Date: 2026-07-12 14:36:28.449531

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6ac532b339da'
down_revision: Union[str, Sequence[str], None] = '8fa0f51a9543'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Create new enums in database
    licensecategory_enum = postgresql.ENUM('LMV', 'HMV', 'MCWG', 'Transport', 'Heavy_Transport', 'Other', name='licensecategory_enum')
    licensecategory_enum.create(op.get_bind(), checkfirst=True)

    driverstatus_enum = postgresql.ENUM('AVAILABLE', 'ON_TRIP', 'OFF_DUTY', 'SUSPENDED', name='driverstatus_enum')
    driverstatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add new columns
    op.add_column('drivers', sa.Column('full_name', sa.String(length=100), nullable=False))
    op.add_column('drivers', sa.Column('license_category', sa.Enum('LMV', 'HMV', 'MCWG', 'Transport', 'Heavy_Transport', 'Other', name='licensecategory_enum'), nullable=False))
    op.add_column('drivers', sa.Column('license_expiry_date', sa.Date(), nullable=False))
    op.add_column('drivers', sa.Column('contact_number', sa.String(length=20), nullable=False))
    op.add_column('drivers', sa.Column('safety_score', sa.Integer(), nullable=False))
    
    # 3. Drop old status column and recreate
    op.drop_index('ix_drivers_status', table_name='drivers')
    op.drop_column('drivers', 'status')
    op.add_column('drivers', sa.Column('status', sa.Enum('AVAILABLE', 'ON_TRIP', 'OFF_DUTY', 'SUSPENDED', name='driverstatus_enum'), nullable=False))

    # 4. Clean up old unique constraints & indices and make new ones
    op.drop_index('ix_drivers_license_expiry', table_name='drivers')
    op.create_index(op.f('ix_drivers_license_expiry_date'), 'drivers', ['license_expiry_date'], unique=False)
    op.create_index(op.f('ix_drivers_license_number'), 'drivers', ['license_number'], unique=True)
    op.create_index(op.f('ix_drivers_status'), 'drivers', ['status'], unique=False)
    
    # 5. Drop old columns
    op.drop_column('drivers', 'license_expiry')


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Drop new columns and indexes
    op.drop_index(op.f('ix_drivers_status'), table_name='drivers')
    op.drop_index(op.f('ix_drivers_license_number'), table_name='drivers')
    op.drop_index(op.f('ix_drivers_license_expiry_date'), table_name='drivers')
    op.drop_column('drivers', 'status')

    # 2. Recreate old status column and indexes
    op.add_column('drivers', sa.Column('status', postgresql.ENUM('ACTIVE', 'ON_TRIP', 'INACTIVE', 'SUSPENDED', name='driverstatus'), nullable=False))
    op.create_index('ix_drivers_status', 'drivers', ['status'], unique=False)

    op.add_column('drivers', sa.Column('license_expiry', sa.DATE(), autoincrement=False, nullable=False))
    op.create_index('ix_drivers_license_expiry', 'drivers', ['license_expiry'], unique=False)

    # 3. Drop new columns
    op.drop_column('drivers', 'safety_score')
    op.drop_column('drivers', 'contact_number')
    op.drop_column('drivers', 'license_expiry_date')
    op.drop_column('drivers', 'license_category')
    op.drop_column('drivers', 'full_name')

    # 4. Drop new enum types
    postgresql.ENUM(name='licensecategory_enum').drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name='driverstatus_enum').drop(op.get_bind(), checkfirst=True)
