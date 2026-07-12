import enum

class VehicleStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ON_TRIP = "ON_TRIP"
    IN_SHOP = "IN_SHOP"
    RETIRED = "RETIRED"

class VehicleType(str, enum.Enum):
    Truck = "Truck"
    Van = "Van"
    Pickup = "Pickup"
    Mini_Truck = "Mini Truck"
    Bus = "Bus"
    Other = "Other"

class DriverStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    ON_TRIP = "ON_TRIP"
    OFF_DUTY = "OFF_DUTY"
    SUSPENDED = "SUSPENDED"

class LicenseCategory(str, enum.Enum):
    LMV = "LMV"
    HMV = "HMV"
    MCWG = "MCWG"
    Transport = "Transport"
    Heavy_Transport = "Heavy Transport"
    Other = "Other"
