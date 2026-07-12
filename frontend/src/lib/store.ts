import { useSyncExternalStore } from "react";

export type VehicleStatus = "Available" | "On Trip" | "In Shop" | "Retired";
export type DriverStatus = "Available" | "On Trip" | "Off Duty" | "Suspended";
export type TripStatus = "Draft" | "Dispatched" | "Completed" | "Cancelled";
export type Role = "Fleet Manager" | "Dispatcher" | "Safety Officer" | "Financial Analyst";

export interface Vehicle {
  id: string;
  registration: string;
  name: string;
  type: string;
  capacity: number; // kg
  odometer: number;
  cost: number;
  status: VehicleStatus;
}
export interface Driver {
  id: string;
  name: string;
  license: string;
  category: string;
  licenseExpiry: string; // ISO
  contact: string;
  safetyScore: number;
  status: DriverStatus;
}
export interface Trip {
  id: string;
  source: string;
  destination: string;
  vehicleId: string;
  driverId: string;
  cargoWeight: number;
  distance: number;
  status: TripStatus;
  createdAt: string;
  revenue?: number;
  fuelConsumed?: number;
  finalOdometer?: number;
}
export interface MaintenanceLog {
  id: string;
  vehicleId: string;
  type: string;
  cost: number;
  date: string;
  status: "Active" | "Completed";
  notes?: string;
}
export interface FuelLog {
  id: string;
  vehicleId: string;
  liters: number;
  cost: number;
  date: string;
  station?: string;
}
export interface Expense {
  id: string;
  tripId?: string;
  category: "Tolls" | "Misc" | "Consumables" | "Parking" | "Other";
  amount: number;
  description: string;
  date: string;
}
export interface User {
  id: string;
  name: string;
  email: string;
  password?: string;
  role: Role;
}
export interface Session {
  userId: string;
}

interface DB {
  users: User[];
  session: Session | null;
  vehicles: Vehicle[];
  drivers: Driver[];
  trips: Trip[];
  maintenance: MaintenanceLog[];
  fuel: FuelLog[];
  expenses: Expense[];
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getHeaders() {
  const token = localStorage.getItem("transitops_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request(path: string, options: RequestInit = {}) {
  const url = `${API_BASE_URL}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  });
  if (response.status === 401) {
    localStorage.removeItem("transitops_token");
    db = { ...db, session: null };
    emit();
    throw new Error("Session expired or unauthorized. Please sign in again.");
  }
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

function mapVehicleStatusToFE(s: string): VehicleStatus {
  if (s === "AVAILABLE") return "Available";
  if (s === "ON_TRIP") return "On Trip";
  if (s === "IN_SHOP") return "In Shop";
  if (s === "RETIRED") return "Retired";
  return s as any;
}

function mapVehicleStatusToBE(s: string): string {
  if (s === "Available") return "AVAILABLE";
  if (s === "On Trip") return "ON_TRIP";
  if (s === "In Shop") return "IN_SHOP";
  if (s === "Retired") return "RETIRED";
  return s;
}

function mapVehicleTypeToBE(t: string): string {
  const lower = t.toLowerCase();
  if (lower.includes("truck")) {
    if (lower.includes("mini")) return "Mini Truck";
    return "Truck";
  }
  if (lower.includes("van")) return "Van";
  if (lower.includes("pickup")) return "Pickup";
  if (lower.includes("bus")) return "Bus";
  return "Other";
}

function mapDriverStatusToFE(s: string): DriverStatus {
  if (s === "AVAILABLE") return "Available";
  if (s === "ON_TRIP") return "On Trip";
  if (s === "OFF_DUTY") return "Off Duty";
  if (s === "SUSPENDED") return "Suspended";
  return s as any;
}

function mapDriverStatusToBE(s: string): string {
  if (s === "Available") return "AVAILABLE";
  if (s === "On Trip") return "ON_TRIP";
  if (s === "Off Duty") return "OFF_DUTY";
  if (s === "Suspended") return "SUSPENDED";
  return s;
}

function mapLicenseCategoryToBE(c: string): string {
  const valid = ["LMV", "HMV", "MCWG", "Transport", "Heavy Transport", "Other"];
  if (valid.includes(c)) return c;
  if (c.toLowerCase() === "heavy transport") return "Heavy Transport";
  return "Other";
}

function mapTripStatusToFE(s: string): TripStatus {
  if (s === "DRAFT") return "Draft";
  if (s === "DISPATCHED") return "Dispatched";
  if (s === "COMPLETED") return "Completed";
  if (s === "CANCELLED") return "Cancelled";
  return s as any;
}

function mapExpenseCategoryToBE(cat: string): string {
  if (cat === "Tolls") return "TOLL";
  if (cat === "Parking") return "PARKING";
  return "OTHER";
}

function mapExpenseCategoryToFE(type: string): "Tolls" | "Misc" | "Consumables" | "Parking" | "Other" {
  if (type === "TOLL") return "Tolls";
  if (type === "PARKING") return "Parking";
  return "Other";
}

function seed(): DB {
  return {
    users: [],
    session: null,
    vehicles: [],
    drivers: [],
    trips: [],
    maintenance: [],
    fuel: [],
    expenses: [],
  };
}

let db: DB = seed();
const listeners = new Set<() => void>();
let hydrated = false;

function emit() {
  listeners.forEach((l) => l());
}

async function initSession() {
  const token = localStorage.getItem("transitops_token");
  if (token) {
    try {
      const user = await request("/api/auth/me");
      db = {
        ...db,
        users: [user],
        session: { userId: user.id }
      };
      emit();
      await actions.loadAll();
    } catch {
      localStorage.removeItem("transitops_token");
      db = { ...db, session: null };
      emit();
    }
  }
}

if (typeof window !== "undefined") {
  setTimeout(initSession, 0);
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => listeners.delete(cb);
}

export function useDB<T>(selector: (d: DB) => T): T {
  return useSyncExternalStore(
    subscribe,
    () => selector(db),
    () => selector(db),
  );
}

export const actions = {
  reset() {
    db = seed();
    localStorage.removeItem("transitops_token");
    emit();
  },

  async loadAll() {
    const token = localStorage.getItem("transitops_token");
    if (!token) return;
    try {
      const [vehiclesData, driversData, tripsData, maintenanceData, fuelData, expensesData] = await Promise.all([
        request("/api/v1/vehicles/?limit=100"),
        request("/api/v1/drivers/?limit=100"),
        request("/api/v1/trips/?limit=100"),
        request("/api/v1/maintenance/?limit=100"),
        request("/api/v1/fuel-logs/?limit=100"),
        request("/api/v1/expenses/?limit=100"),
      ]);

      const vehicles = (vehiclesData.items || []).map((v: any) => ({
        id: v.id,
        registration: v.registration_number,
        name: v.vehicle_name,
        type: v.vehicle_type,
        capacity: v.maximum_load_capacity,
        odometer: v.odometer,
        cost: Number(v.acquisition_cost),
        status: mapVehicleStatusToFE(v.status),
      }));

      const drivers = (driversData.items || []).map((d: any) => ({
        id: d.id,
        name: d.full_name,
        license: d.license_number,
        category: d.license_category,
        licenseExpiry: d.license_expiry_date,
        contact: d.contact_number,
        safetyScore: d.safety_score,
        status: mapDriverStatusToFE(d.status),
      }));

      const trips = (tripsData.items || []).map((t: any) => ({
        id: t.id,
        source: t.source,
        destination: t.destination,
        vehicleId: t.vehicle_id,
        driverId: t.driver_id,
        cargoWeight: t.cargo_weight,
        distance: t.planned_distance,
        status: mapTripStatusToFE(t.status),
        createdAt: t.created_at,
        fuelConsumed: t.fuel_consumed,
        finalOdometer: t.final_odometer,
      }));

      const maintenance = (maintenanceData.items || []).map((m: any) => ({
        id: m.id,
        vehicleId: m.vehicle_id,
        type: m.maintenance_type,
        cost: m.cost,
        date: m.start_date,
        status: m.status === "ACTIVE" ? "Active" : "Completed",
        notes: m.description,
      }));

      const fuel = (fuelData.items || []).map((f: any) => ({
        id: f.id,
        vehicleId: f.vehicle_id,
        liters: f.liters,
        cost: f.cost,
        date: f.fuel_date,
      }));

      const expenses = (expensesData.items || []).map((e: any) => ({
        id: e.id,
        category: mapExpenseCategoryToFE(e.expense_type),
        amount: e.amount,
        description: e.description,
        date: e.expense_date,
      }));

      db = {
        ...db,
        vehicles,
        drivers,
        trips,
        maintenance,
        fuel,
        expenses,
      };
      emit();
    } catch (err) {
      console.error("Failed to load all data from backend", err);
    }
  },

  async signup(u: Omit<User, "id">) {
    await request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({
        name: u.name,
        email: u.email,
        password: u.password,
        role: u.role,
      }),
    });
    return actions.login(u.email, u.password!);
  },

  async login(email: string, password: string) {
    const data = await request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    localStorage.setItem("transitops_token", data.access_token);
    const user: User = {
      id: data.user.id,
      name: data.user.name,
      email: data.user.email,
      role: data.user.role,
    };

    db = {
      ...db,
      users: [user],
      session: { userId: user.id },
    };
    emit();
    await actions.loadAll();
    return user;
  },

  logout() {
    localStorage.removeItem("transitops_token");
    db = seed();
    emit();
  },

  async addVehicle(v: Omit<Vehicle, "id">) {
    await request("/api/v1/vehicles/", {
      method: "POST",
      body: JSON.stringify({
        registration_number: v.registration,
        vehicle_name: v.name,
        vehicle_model: v.name,
        vehicle_type: mapVehicleTypeToBE(v.type),
        maximum_load_capacity: v.capacity,
        odometer: v.odometer,
        acquisition_cost: v.cost,
        status: mapVehicleStatusToBE(v.status),
      }),
    });
    await actions.loadAll();
  },

  async updateVehicle(id: string, patch: Partial<Vehicle>) {
    const payload: any = {};
    if (patch.registration !== undefined) payload.registration_number = patch.registration;
    if (patch.name !== undefined) {
      payload.vehicle_name = patch.name;
      payload.vehicle_model = patch.name;
    }
    if (patch.type !== undefined) payload.vehicle_type = mapVehicleTypeToBE(patch.type);
    if (patch.capacity !== undefined) payload.maximum_load_capacity = patch.capacity;
    if (patch.odometer !== undefined) payload.odometer = patch.odometer;
    if (patch.cost !== undefined) payload.acquisition_cost = patch.cost;
    if (patch.status !== undefined) payload.status = mapVehicleStatusToBE(patch.status);

    await request(`/api/v1/vehicles/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await actions.loadAll();
  },

  async deleteVehicle(id: string) {
    await request(`/api/v1/vehicles/${id}`, {
      method: "DELETE",
    });
    await actions.loadAll();
  },

  async addDriver(d: Omit<Driver, "id">) {
    const contact = d.contact.replace(/[^\d+]/g, '');
    await request("/api/v1/drivers/", {
      method: "POST",
      body: JSON.stringify({
        full_name: d.name,
        license_number: d.license,
        license_category: mapLicenseCategoryToBE(d.category),
        license_expiry_date: d.licenseExpiry.split("T")[0],
        contact_number: contact.length >= 10 ? contact : "1234567890",
        safety_score: d.safetyScore,
        status: mapDriverStatusToBE(d.status),
      }),
    });
    await actions.loadAll();
  },

  async updateDriver(id: string, patch: Partial<Driver>) {
    const payload: any = {};
    if (patch.name !== undefined) payload.full_name = patch.name;
    if (patch.license !== undefined) payload.license_number = patch.license;
    if (patch.category !== undefined) payload.license_category = mapLicenseCategoryToBE(patch.category);
    if (patch.licenseExpiry !== undefined) payload.license_expiry_date = patch.licenseExpiry.split("T")[0];
    if (patch.contact !== undefined) {
      const contact = patch.contact.replace(/[^\d+]/g, '');
      payload.contact_number = contact.length >= 10 ? contact : "1234567890";
    }
    if (patch.safetyScore !== undefined) payload.safety_score = patch.safetyScore;
    if (patch.status !== undefined) payload.status = mapDriverStatusToBE(patch.status);

    await request(`/api/v1/drivers/${id}`, {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    await actions.loadAll();
  },

  async deleteDriver(id: string) {
    await request(`/api/v1/drivers/${id}`, {
      method: "DELETE",
    });
    await actions.loadAll();
  },

  async createTrip(t: Omit<Trip, "id" | "status" | "createdAt">) {
    const trip = await request("/api/v1/trips/", {
      method: "POST",
      body: JSON.stringify({
        source: t.source,
        destination: t.destination,
        vehicle_id: t.vehicleId,
        driver_id: t.driverId,
        cargo_weight: t.cargoWeight,
        planned_distance: t.distance,
      }),
    });
    await actions.loadAll();
    return {
      id: trip.id,
      source: trip.source,
      destination: trip.destination,
      vehicleId: trip.vehicle_id,
      driverId: trip.driver_id,
      cargoWeight: trip.cargo_weight,
      distance: trip.planned_distance,
      status: mapTripStatusToFE(trip.status),
      createdAt: trip.created_at,
    };
  },

  async dispatchTrip(id: string) {
    await request(`/api/v1/trips/${id}/dispatch`, {
      method: "POST",
    });
    await actions.loadAll();
  },

  async completeTrip(id: string, finalOdometer?: number, fuelConsumed?: number) {
    await request(`/api/v1/trips/${id}/complete`, {
      method: "POST",
      body: JSON.stringify({
        final_odometer: finalOdometer,
        fuel_consumed: fuelConsumed,
      }),
    });
    await actions.loadAll();
  },

  async cancelTrip(id: string) {
    await request(`/api/v1/trips/${id}/cancel`, {
      method: "POST",
    });
    await actions.loadAll();
  },

  async addMaintenance(m: Omit<MaintenanceLog, "id">) {
    await request("/api/v1/maintenance/", {
      method: "POST",
      body: JSON.stringify({
        vehicle_id: m.vehicleId,
        maintenance_type: m.type,
        description: m.notes || "No description provided",
        start_date: m.date.split("T")[0],
        cost: m.cost,
        status: m.status === "Active" ? "ACTIVE" : "COMPLETED",
      }),
    });
    await actions.loadAll();
  },

  async closeMaintenance(id: string) {
    await request(`/api/v1/maintenance/${id}/close`, {
      method: "POST",
    });
    await actions.loadAll();
  },

  async addFuel(f: Omit<FuelLog, "id">) {
    const vehicle = db.vehicles.find((v) => v.id === f.vehicleId);
    const odometer = vehicle ? vehicle.odometer : 0;
    await request("/api/v1/fuel-logs/", {
      method: "POST",
      body: JSON.stringify({
        vehicle_id: f.vehicleId,
        fuel_date: f.date || new Date().toISOString().split("T")[0],
        liters: f.liters,
        cost: f.cost,
        odometer: odometer,
      }),
    });
    await actions.loadAll();
  },

  async addExpense(e: Omit<Expense, "id">) {
    let vehicleId = "00000000-0000-0000-0000-000000000000";
    if (e.tripId) {
      const trip = db.trips.find((t) => t.id === e.tripId);
      if (trip && trip.vehicleId) {
        vehicleId = trip.vehicleId;
      }
    } else {
      const firstVehicle = db.vehicles[0];
      if (firstVehicle) vehicleId = firstVehicle.id;
    }
    await request("/api/v1/expenses/", {
      method: "POST",
      body: JSON.stringify({
        vehicle_id: vehicleId,
        expense_type: mapExpenseCategoryToBE(e.category),
        amount: e.amount,
        description: e.description,
        expense_date: e.date || new Date().toISOString().split("T")[0],
      }),
    });
    await actions.loadAll();
  },
};

export function currentUser(): User | null {
  if (!db.session) return null;
  return db.users.find((u) => u.id === db.session!.userId) ?? null;
}
