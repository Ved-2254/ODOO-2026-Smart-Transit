import os
from typing import List, Union
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

# Explicitly load .env file, overriding any existing shell environment variables
load_dotenv(override=True)

class Settings(BaseModel):
    PROJECT_NAME: str = "TransitOps API"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "local")
    
    # Required variables
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []

    @field_validator("DATABASE_URL", "SECRET_KEY")
    @classmethod
    def validate_required(cls, v: str, info) -> str:
        if not v or v.strip() == "":
            raise ValueError(f"{info.field_name} must be set in the environment or .env file")
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str], None]) -> List[str]:
        if not v:
            return ["http://localhost:5173"]  # Default allowed origin
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]

# Initialize and validate settings
settings = Settings(
    BACKEND_CORS_ORIGINS=os.getenv("BACKEND_CORS_ORIGINS", "")
)
