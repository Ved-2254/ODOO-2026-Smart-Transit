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

@pytest.fixture
def valid_vehicle_payload():
    unique_reg = f"TX-{uuid.uuid4().hex[:6].upper()}"
    return {
        "registration_number": unique_reg,
        "vehicle_name": "Tesla Semi",
        "vehicle_model": "Semi 2024",
        "vehicle_type": "Truck",
        "maximum_load_capacity": 36000.0,
        "odometer": 1500.0,
        "acquisition_cost": "180000.00",
        "status": "AVAILABLE"
    }

# 1. Create vehicle (valid request, duplicates rejected)
def test_create_vehicle_success(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["registration_number"] == valid_vehicle_payload["registration_number"]
    assert data["vehicle_name"] == valid_vehicle_payload["vehicle_name"]
    assert data["status"] == "AVAILABLE"

def test_create_vehicle_duplicate_registration(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create first
    response1 = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert response1.status_code == 201
    
    # Create duplicate
    response2 = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert response2.status_code == 409
    assert "Duplicate registration number" in response2.json()["detail"]

# 2. Update vehicle (valid changes, unique constraint checks)
def test_update_vehicle_success(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create first
    create_res = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert create_res.status_code == 201
    vehicle_id = create_res.json()["id"]
    
    # Update name and odometer
    update_payload = {
        "vehicle_name": "Tesla Semi Updated",
        "odometer": 2000.0
    }
    update_res = client.put(f"/api/v1/vehicles/{vehicle_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["vehicle_name"] == "Tesla Semi Updated"
    assert data["odometer"] == 2000.0
    assert data["registration_number"] == valid_vehicle_payload["registration_number"]

def test_update_vehicle_duplicate_registration(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    # Create vehicle A
    res_a = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert res_a.status_code == 201
    
    # Create vehicle B
    payload_b = valid_vehicle_payload.copy()
    payload_b["registration_number"] = f"TX-{uuid.uuid4().hex[:6].upper()}"
    res_b = client.post("/api/v1/vehicles/", json=payload_b, headers=headers)
    assert res_b.status_code == 201
    vehicle_b_id = res_b.json()["id"]
    
    # Try updating vehicle B's registration to vehicle A's registration
    update_payload = {
        "registration_number": valid_vehicle_payload["registration_number"]
    }
    response = client.put(f"/api/v1/vehicles/{vehicle_b_id}", json=update_payload, headers=headers)
    assert response.status_code == 409
    assert "Duplicate registration number" in response.json()["detail"]

# 3. Delete vehicle (successful delete vs block if ON_TRIP)
def test_delete_vehicle_success(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create
    create_res = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert create_res.status_code == 201
    vehicle_id = create_res.json()["id"]
    
    # Delete
    delete_res = client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
    assert delete_res.status_code == 204
    
    # Verify 404
    get_res = client.get(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
    assert get_res.status_code == 404

def test_delete_vehicle_on_trip_fails(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create as ON_TRIP
    payload = valid_vehicle_payload.copy()
    payload["status"] = "ON_TRIP"
    create_res = client.post("/api/v1/vehicles/", json=payload, headers=headers)
    assert create_res.status_code == 201
    vehicle_id = create_res.json()["id"]
    
    # Try to Delete
    delete_res = client.delete(f"/api/v1/vehicles/{vehicle_id}", headers=headers)
    assert delete_res.status_code == 409
    assert "cannot be deleted because it is On Trip" in delete_res.json()["detail"]

# 4. Filters (status, type, combined)
def test_filter_vehicles(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    # Create vehicle A (AVAILABLE, Van)
    payload_a = valid_vehicle_payload.copy()
    payload_a["registration_number"] = f"TX-{uuid.uuid4().hex[:6].upper()}"
    payload_a["status"] = "AVAILABLE"
    payload_a["vehicle_type"] = "Van"
    client.post("/api/v1/vehicles/", json=payload_a, headers=headers)
    
    # Create vehicle B (IN_SHOP, Truck)
    payload_b = valid_vehicle_payload.copy()
    payload_b["registration_number"] = f"TX-{uuid.uuid4().hex[:6].upper()}"
    payload_b["status"] = "IN_SHOP"
    payload_b["vehicle_type"] = "Truck"
    client.post("/api/v1/vehicles/", json=payload_b, headers=headers)
    
    # Filter by status
    res_status = client.get("/api/v1/vehicles/?status=IN_SHOP", headers=headers)
    assert res_status.status_code == 200
    assert any(x["registration_number"] == payload_b["registration_number"] for x in res_status.json()["items"])
    assert not any(x["registration_number"] == payload_a["registration_number"] for x in res_status.json()["items"])
    
    # Filter by vehicle_type
    res_type = client.get("/api/v1/vehicles/?vehicle_type=Van", headers=headers)
    assert res_type.status_code == 200
    assert any(x["registration_number"] == payload_a["registration_number"] for x in res_type.json()["items"])
    assert not any(x["registration_number"] == payload_b["registration_number"] for x in res_type.json()["items"])

# 5. Search
def test_search_vehicles(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    payload = valid_vehicle_payload.copy()
    unique_id = uuid.uuid4().hex[:6]
    payload["registration_number"] = f"SRCH-{unique_id}"
    payload["vehicle_name"] = f"Tesla Truck {unique_id}"
    payload["vehicle_model"] = f"SemiModel-{unique_id}"
    client.post("/api/v1/vehicles/", json=payload, headers=headers)
    
    # Search by registration
    res1 = client.get(f"/api/v1/vehicles/?search=SRCH-{unique_id}", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["total"] == 1
    
    # Search by vehicle_name
    res2 = client.get(f"/api/v1/vehicles/?search=Tesla Truck {unique_id}", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["total"] == 1

# 6. Pagination
def test_pagination_vehicles(tokens):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/vehicles/?page=1&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) <= 2

# 7. Sorting
def test_sorting_vehicles(tokens):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/vehicles/?sort_by=registration_number&order=asc", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    if len(items) >= 2:
        assert items[0]["registration_number"] <= items[1]["registration_number"]

# 8. Unauthorized access (Missing JWT or invalid JWT)
def test_unauthorized_access():
    response = client.get("/api/v1/vehicles/")
    assert response.status_code == 401
    
    headers = {"Authorization": "Bearer invalidjwttoken"}
    response2 = client.get("/api/v1/vehicles/", headers=headers)
    assert response2.status_code == 401

# 9. Forbidden RBAC access (Driver role)
def test_forbidden_rbac_access_driver(tokens, valid_vehicle_payload):
    headers = {"Authorization": f"Bearer {tokens['Driver']}"}
    
    # Read access forbidden
    res_get = client.get("/api/v1/vehicles/", headers=headers)
    assert res_get.status_code == 403
    
    # Write access forbidden
    res_post = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers)
    assert res_post.status_code == 403

# 10. Safety Officer / Financial Analyst Read Only Allowed, Forbidden Write
def test_read_only_roles_forbidden_write(tokens, valid_vehicle_payload):
    # Safety Officer
    headers_so = {"Authorization": f"Bearer {tokens['Safety Officer']}"}
    res_get_so = client.get("/api/v1/vehicles/", headers=headers_so)
    assert res_get_so.status_code == 200
    res_post_so = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers_so)
    assert res_post_so.status_code == 403
    
    # Financial Analyst
    headers_fa = {"Authorization": f"Bearer {tokens['Financial Analyst']}"}
    res_get_fa = client.get("/api/v1/vehicles/", headers=headers_fa)
    assert res_get_fa.status_code == 200
    res_post_fa = client.post("/api/v1/vehicles/", json=valid_vehicle_payload, headers=headers_fa)
    assert res_post_fa.status_code == 403
