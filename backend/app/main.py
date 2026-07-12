from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title="TransitOps API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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

@app.get("/")
def read_root():
    return {
        "status": "Backend Running"
    }
