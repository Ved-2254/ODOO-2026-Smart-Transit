"""add_phase8_fuel_expense_updates

Revision ID: b8e4f2a71c05
Revises: a67fedbb1b36
Create Date: 2026-07-12 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8e4f2a71c05'
down_revision: Union[str, Sequence[str], None] = 'a67fedbb1b36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for Phase 8 – Fuel & Expense Module."""

    # ── fuel_logs table changes ──────────────────────────────────────────

    # 1. Rename columns to match Phase 8 spec
    op.alter_column('fuel_logs', 'fuel_quantity', new_column_name='liters')
    op.alter_column('fuel_logs', 'price_per_unit', new_column_name='cost')
    op.alter_column('fuel_logs', 'odometer_at_fill', new_column_name='odometer')
    op.alter_column('fuel_logs', 'fill_date', new_column_name='fuel_date')

    # 2. Add trip_id FK column
    op.add_column('fuel_logs', sa.Column('trip_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        'fk_fuel_logs_trip_id_trips',
        'fuel_logs', 'trips',
        ['trip_id'], ['id'],
        ondelete='SET NULL'
    )

    # 3. Drop old check constraints and create new ones with updated column names
    op.drop_constraint('check_fuel_quantity_non_negative', 'fuel_logs', type_='check')
    op.drop_constraint('check_fuel_price_non_negative', 'fuel_logs', type_='check')
    op.drop_constraint('check_fuel_odometer_non_negative', 'fuel_logs', type_='check')

    op.create_check_constraint('check_fuel_liters_positive', 'fuel_logs', 'liters > 0')
    op.create_check_constraint('check_fuel_cost_non_negative', 'fuel_logs', 'cost >= 0')
    op.create_check_constraint('check_fuel_odometer_non_negative', 'fuel_logs', 'odometer >= 0')

    # ── expenses table changes ───────────────────────────────────────────

    # 4. Make vehicle_id non-nullable (Phase 8: vehicle must exist)
    op.alter_column('expenses', 'vehicle_id',
        existing_type=sa.UUID(),
        nullable=False
    )

    # 5. Update the FK constraint from SET NULL to CASCADE for vehicle_id
    op.drop_constraint('expenses_vehicle_id_fkey', 'expenses', type_='foreignkey')
    op.create_foreign_key(
        'expenses_vehicle_id_fkey',
        'expenses', 'vehicles',
        ['vehicle_id'], ['id'],
        ondelete='CASCADE'
    )

    # 6. Add PARKING to the expensetype enum
    #    PostgreSQL ALTER TYPE ... ADD VALUE is not transactional, so we execute it directly.
    op.execute("ALTER TYPE expensetype ADD VALUE IF NOT EXISTS 'PARKING'")


def downgrade() -> None:
    """Downgrade schema – reverse Phase 8 changes."""

    # ── expenses table changes ───────────────────────────────────────────

    # Revert vehicle_id FK back to SET NULL
    op.drop_constraint('expenses_vehicle_id_fkey', 'expenses', type_='foreignkey')
    op.create_foreign_key(
        'expenses_vehicle_id_fkey',
        'expenses', 'vehicles',
        ['vehicle_id'], ['id'],
        ondelete='SET NULL'
    )

    # Revert vehicle_id back to nullable
    op.alter_column('expenses', 'vehicle_id',
        existing_type=sa.UUID(),
        nullable=True
    )

    # Note: PostgreSQL does not support removing values from an enum type easily.
    # PARKING will remain in the enum on downgrade.

    # ── fuel_logs table changes ──────────────────────────────────────────

    # Drop new check constraints
    op.drop_constraint('check_fuel_liters_positive', 'fuel_logs', type_='check')
    op.drop_constraint('check_fuel_cost_non_negative', 'fuel_logs', type_='check')
    op.drop_constraint('check_fuel_odometer_non_negative', 'fuel_logs', type_='check')

    # Recreate old check constraints
    op.create_check_constraint('check_fuel_quantity_non_negative', 'fuel_logs', 'fuel_quantity >= 0')
    op.create_check_constraint('check_fuel_price_non_negative', 'fuel_logs', 'price_per_unit >= 0')
    op.create_check_constraint('check_fuel_odometer_non_negative', 'fuel_logs', 'odometer_at_fill >= 0')

    # Drop trip_id FK and column
    op.drop_constraint('fk_fuel_logs_trip_id_trips', 'fuel_logs', type_='foreignkey')
    op.drop_column('fuel_logs', 'trip_id')

    # Rename columns back
    op.alter_column('fuel_logs', 'fuel_date', new_column_name='fill_date')
    op.alter_column('fuel_logs', 'odometer', new_column_name='odometer_at_fill')
    op.alter_column('fuel_logs', 'cost', new_column_name='price_per_unit')
    op.alter_column('fuel_logs', 'liters', new_column_name='fuel_quantity')
