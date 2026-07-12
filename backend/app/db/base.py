# Import all the models, so that Base has them before being
# imported by Alembic or other modules.
from app.db.database import Base  # noqa
from app.models.role import Role  # noqa
from app.models.user import User  # noqa
from app.models.vehicle import Vehicle  # noqa
from app.models.driver import Driver  # noqa
from app.models.trip import Trip  # noqa
from app.models.maintenance import MaintenanceLog  # noqa
from app.models.fuel import FuelLog  # noqa
from app.models.expense import Expense  # noqa
