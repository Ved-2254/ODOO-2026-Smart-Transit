import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr = Field(..., description="Unique email address")
    password: str = Field(..., min_length=8, description="Password with minimum 8 characters")
    role: str = Field(..., min_length=1, max_length=50, description="Role of the user, e.g. Fleet Manager")

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
