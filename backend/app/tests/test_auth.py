import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def unique_user_payload():
    unique_id = uuid.uuid4().hex[:8]
    return {
        "name": f"Test User {unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "securepassword123",
        "role": "Fleet Manager"
    }

def test_register_success(unique_user_payload):
    response = client.post("/api/auth/register", json=unique_user_payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == unique_user_payload["name"]
    assert data["email"] == unique_user_payload["email"]
    assert data["role"] == unique_user_payload["role"]

def test_register_duplicate_email(unique_user_payload):
    # Register once
    response = client.post("/api/auth/register", json=unique_user_payload)
    assert response.status_code == 201
    
    # Register again with same email
    response2 = client.post("/api/auth/register", json=unique_user_payload)
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]

def test_register_invalid_role(unique_user_payload):
    unique_user_payload["role"] = "Non Existent Role"
    response = client.post("/api/auth/register", json=unique_user_payload)
    assert response.status_code == 400
    assert "does not exist" in response.json()["detail"]

def test_register_password_too_short(unique_user_payload):
    unique_user_payload["password"] = "short"
    response = client.post("/api/auth/register", json=unique_user_payload)
    assert response.status_code == 422  # Pydantic validation error (min_length=8)

def test_login_success(unique_user_payload):
    # First, register the user
    client.post("/api/auth/register", json=unique_user_payload)
    
    # Login
    login_data = {
        "email": unique_user_payload["email"],
        "password": unique_user_payload["password"]
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_user_payload["email"]
    assert data["user"]["role"] == unique_user_payload["role"]

def test_login_invalid_credentials(unique_user_payload):
    client.post("/api/auth/register", json=unique_user_payload)
    
    login_data = {
        "email": unique_user_payload["email"],
        "password": "wrongpassword"
    }
    response = client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_me_success(unique_user_payload):
    # Register & Login to get token
    client.post("/api/auth/register", json=unique_user_payload)
    
    login_data = {
        "email": unique_user_payload["email"],
        "password": unique_user_payload["password"]
    }
    login_response = client.post("/api/auth/login", json=login_data)
    token = login_response.json()["access_token"]
    
    # Access /api/auth/me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_user_payload["email"]
    assert data["name"] == unique_user_payload["name"]
    assert data["role"] == unique_user_payload["role"]

def test_get_me_unauthorized():
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    
    headers = {"Authorization": "Bearer invalidtokenhere"}
    response2 = client.get("/api/auth/me", headers=headers)
    assert response2.status_code == 401

def test_get_me_expired_token(unique_user_payload):
    from datetime import timedelta
    from app.core.security import create_access_token
    
    # Register user
    client.post("/api/auth/register", json=unique_user_payload)
    
    # Generate an expired token by passing a negative expires_delta
    token_payload = {
        "user_id": "7a3b4e67-d890-410a-bf12-58e92d6bba78",
        "email": unique_user_payload["email"],
        "role": unique_user_payload["role"]
    }
    expired_token = create_access_token(data=token_payload, expires_delta=timedelta(minutes=-5))
    
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401
    assert "Invalid or expired access token" in response.json()["detail"]

