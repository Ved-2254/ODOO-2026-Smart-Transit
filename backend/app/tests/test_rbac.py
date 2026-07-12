import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def tokens():
    """Register and login one user for each role to acquire authorization tokens."""
    roles = ["Admin", "Fleet Manager", "Driver", "Safety Officer", "Financial Analyst"]
    tokens_map = {}
    
    for role in roles:
        unique_id = uuid.uuid4().hex[:8]
        email = f"user_{unique_id}_{role.replace(' ', '_').lower()}@example.com"
        password = "securepassword123"
        name = f"Test {role} {unique_id}"
        
        # 1. Register
        register_payload = {
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }
        res_reg = client.post("/api/auth/register", json=register_payload)
        assert res_reg.status_code == 201
        
        # 2. Login
        login_payload = {
            "email": email,
            "password": password
        }
        res_login = client.post("/api/auth/login", json=login_payload)
        assert res_login.status_code == 200
        
        tokens_map[role] = res_login.json()["access_token"]
        
    return tokens_map

# =====================================================================
# Tests: GET /api/v1/vehicles & POST /api/v1/vehicles (Fleet Manager, Admin allowed)
# =====================================================================

def test_get_vehicles_authorized_roles(tokens):
    # Fleet Manager
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/vehicles", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()
    
    # Admin
    headers = {"Authorization": f"Bearer {tokens['Admin']}"}
    response = client.get("/api/v1/vehicles", headers=headers)
    assert response.status_code == 200

def test_get_vehicles_unauthorized_roles(tokens):
    # Driver
    headers = {"Authorization": f"Bearer {tokens['Driver']}"}
    response = client.get("/api/v1/vehicles", headers=headers)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_post_vehicles_authorized_roles(tokens):
    import uuid
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    payload = {
        "registration_number": f"TX-{uuid.uuid4().hex[:6].upper()}",
        "vehicle_name": "Volvo Truck",
        "vehicle_model": "VNL 860",
        "vehicle_type": "Truck",
        "maximum_load_capacity": 20000.0,
        "odometer": 500.0,
        "acquisition_cost": "150000.00",
        "status": "AVAILABLE"
    }
    response = client.post("/api/v1/vehicles/", json=payload, headers=headers)
    assert response.status_code == 201
    assert "id" in response.json()

def test_post_vehicles_unauthorized_roles(tokens):
    import uuid
    headers = {"Authorization": f"Bearer {tokens['Driver']}"}
    payload = {
        "registration_number": f"TX-{uuid.uuid4().hex[:6].upper()}",
        "vehicle_name": "Volvo Truck",
        "vehicle_model": "VNL 860",
        "vehicle_type": "Truck",
        "maximum_load_capacity": 20000.0,
        "odometer": 500.0,
        "acquisition_cost": "150000.00",
        "status": "AVAILABLE"
    }
    response = client.post("/api/v1/vehicles/", json=payload, headers=headers)
    assert response.status_code == 403


# =====================================================================
# Tests: GET /api/v1/drivers (Fleet Manager, Safety Officer, Admin allowed)
# =====================================================================

def test_get_drivers_authorized_roles(tokens):
    # Safety Officer
    headers = {"Authorization": f"Bearer {tokens['Safety Officer']}"}
    response = client.get("/api/v1/drivers", headers=headers)
    assert response.status_code == 200
    assert "items" in response.json()
    
    # Fleet Manager
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/drivers", headers=headers)
    assert response.status_code == 200
    
    # Admin
    headers = {"Authorization": f"Bearer {tokens['Admin']}"}
    response = client.get("/api/v1/drivers", headers=headers)
    assert response.status_code == 200

def test_get_drivers_unauthorized_roles(tokens):
    # Driver
    headers = {"Authorization": f"Bearer {tokens['Driver']}"}
    response = client.get("/api/v1/drivers", headers=headers)
    assert response.status_code == 403

# =====================================================================
# Tests: GET /expenses (Financial Analyst, Admin allowed)
# =====================================================================

def test_get_expenses_authorized_roles(tokens):
    # Financial Analyst
    headers = {"Authorization": f"Bearer {tokens['Financial Analyst']}"}
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200
    
    # Admin
    headers = {"Authorization": f"Bearer {tokens['Admin']}"}
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 200

def test_get_expenses_unauthorized_roles(tokens):
    # Fleet Manager
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/expenses", headers=headers)
    assert response.status_code == 403
