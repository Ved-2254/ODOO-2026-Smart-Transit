# Project Status: Phase 1 (Database Layer Setup)

This document summarizes the progress on the database layer setup for the TransitOps FastAPI backend.

## Models Created

We have established 8 SQLAlchemy 2.0 Declarative models mapped to their respective PostgreSQL tables:

1. **`Role`** (`roles`): Defines user permissions roles (e.g. Admin, Driver, Dispatcher).
2. **`User`** (`users`): Main user account credential registry.
3. **`Vehicle`** (`vehicles`): Registry of transit vehicles including make, model, type, and odometer readings.
4. **`Driver`** (`drivers`): Driver profiles linked to their user account, licensing numbers, and expiration dates.
5. **`Trip`** (`trips`): Trip itineraries tracking start/end locations, scheduled timelines, distances, and cargo details.
6. **`MaintenanceLog`** (`maintenance_logs`): Maintenance tracking log for recording repair descriptions and costs.
7. **`FuelLog`** (`fuel_logs`): Logs recording fuel additions, quantities, cost per unit, and odometer markers.
8. **`Expense`** (`expenses`): Financial expense entries associated optionally with vehicles, drivers, or specific trips.

---

## Enums Defined

Custom mapping enums were created to enforce strict validation across the database layer:

- **`VehicleType`**: `TRUCK`, `VAN`, `BUS`, `CAR`, `TRAILER`
- **`VehicleStatus`**: `ACTIVE`, `IN_MAINTENANCE`, `OUT_OF_SERVICE`
- **`DriverStatus`**: `ACTIVE`, `ON_TRIP`, `INACTIVE`, `SUSPENDED`
- **`TripStatus`**: `SCHEDULED`, `IN_TRANSIT`, `COMPLETED`, `CANCELLED`
- **`MaintenanceStatus`**: `SCHEDULED`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`
- **`ExpenseType`**: `FUEL`, `MAINTENANCE`, `TOLL`, `SALARY`, `INSURANCE`, `OTHER`

---

## Relationships

SQLAlchemy relationships were linked between models for easy property loading and referential integrity:

- **`Role` <-> `User`**: One-to-many relationship (a Role has many Users, User has a Foreign Key `role_id`).
- **`User` <-> `Driver`**: One-to-one relationship (User has one Driver profile, Driver has a Unique Foreign Key `user_id`).
- **`Vehicle` <-> `Trip`**: One-to-many relationship (a Vehicle has many Trips).
- **`Vehicle` <-> `MaintenanceLog`**: One-to-many relationship (a Vehicle has many Maintenance logs).
- **`Vehicle` <-> `FuelLog`**: One-to-many relationship (a Vehicle has many Fuel logs).
- **`Vehicle` <-> `Expense`**: One-to-many relationship (a Vehicle has many Expenses).
- **`Driver` <-> `Trip`**: One-to-many relationship (a Driver has many Trips).
- **`Driver` <-> `FuelLog`**: One-to-many relationship (a Driver has many Fuel logs).
- **`Driver` <-> `Expense`**: One-to-many relationship (a Driver has many Expenses).
- **`Trip` <-> `Expense`**: One-to-many relationship (a Trip has many Expenses).

---

## Constraints & Indexes

We configured database constraints and indices for optimal queries, data integrity, and positive values:

### Unique Constraints
- `roles.name` (Unique)
- `users.email` (Unique)
- `drivers.license_number` (Unique)
- `drivers.user_id` (Unique - enforces 1-to-1 profile mapping)
- `vehicles.registration_number` (Unique)

### Check Constraints (Positive Value Validations)
- **`vehicles`**:
  - `capacity > 0` (`check_vehicle_capacity_positive`)
  - `odometer >= 0` (`check_vehicle_odometer_non_negative`)
- **`trips`**:
  - `cargo_weight >= 0` (`check_trip_cargo_weight_non_negative`)
  - `distance >= 0` (`check_trip_distance_non_negative`)
- **`maintenance_logs`**:
  - `cost >= 0` (`check_maintenance_cost_non_negative`)
- **`fuel_logs`**:
  - `fuel_quantity >= 0` (`check_fuel_quantity_non_negative`)
  - `price_per_unit >= 0` (`check_fuel_price_non_negative`)
  - `odometer_at_fill >= 0` (`check_fuel_odometer_non_negative`)
- **`expenses`**:
  - `amount >= 0` (`check_expense_amount_non_negative`)

### Frequently Queried Indices
- `users.email` (Unique Index)
- `roles.name` (Unique Index)
- `vehicles.registration_number` (Unique Index)
- `vehicles.status` (Index)
- `drivers.status` (Index)
- `drivers.license_expiry` (Index)
- `trips.status` (Index)

---

## Migration Status

- **Alembic autogenerate**: Executed successfully.
- **Migration file**: Created under `alembic/versions/e8d69933f700_create_initial_schema.py`.
- **Database upgrade**: Applied to the Supabase PostgreSQL database successfully.

---

## Pending Work

- Initial data seeding (creating default Role items like `admin`, `dispatcher`, `driver`).
- CRUD services layer implementation.
- API endpoints/routes configuration.
