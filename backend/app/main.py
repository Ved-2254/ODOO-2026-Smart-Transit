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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed roles
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
# Explicitly allow http://localhost:5173
origins = ["http://localhost:5173"]

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


@app.get("/")
def read_root():
    return {
        "status": "Backend Running"
    }

