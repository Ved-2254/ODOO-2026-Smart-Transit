from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import SessionLocal
from app.db.seed import seed_roles
from app.api.auth import router as auth_router
from app.api.vehicles import router as vehicles_router
from app.api.drivers import router as drivers_router
from app.api.expenses import router as expenses_router
from app.api.trips import router as trips_router
from app.api.maintenance import router as maintenance_router
from app.api.fuel_logs import router as fuel_logs_router
from app.api.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables exist (for SQLite fallback)
    from app.db.database import Base, engine
    Base.metadata.create_all(bind=engine)

    # Startup: seed roles and admin user
    db = SessionLocal()
    try:
        seed_roles(db)
    finally:
        db.close()
    yield
    # Shutdown (no-op)

app = FastAPI(
    title="TransitOps API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
# Explicitly allow local development origins (localhost and 127.0.0.1 across common ports)
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# Add additional configured origins if present
if settings.BACKEND_CORS_ORIGINS:
    for origin in settings.BACKEND_CORS_ORIGINS:
        if origin not in origins:
            origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(vehicles_router)
app.include_router(drivers_router)
app.include_router(expenses_router)
app.include_router(trips_router)
app.include_router(maintenance_router)
app.include_router(fuel_logs_router)
app.include_router(dashboard_router)



@app.get("/")
def read_root():
    return {
        "status": "Backend Running"
    }

