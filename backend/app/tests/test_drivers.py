import uuid
import pytest
from datetime import date, timedelta
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
def valid_driver_payload():
    unique_lic = f"LIC-{uuid.uuid4().hex[:8].upper()}"
    expiry_date = date.today() + timedelta(days=365)
    return {
        "full_name": "Alex Rodriguez",
        "license_number": unique_lic,
        "license_category": "HMV",
        "license_expiry_date": expiry_date.isoformat(),
        "contact_number": "1234567890",
        "safety_score": 85,
        "status": "AVAILABLE"
    }

# 1. Create driver (valid request, duplicates rejected)
def test_create_driver_success(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["full_name"] == valid_driver_payload["full_name"]
    assert data["license_number"] == valid_driver_payload["license_number"]
    assert data["status"] == "AVAILABLE"

def test_create_driver_duplicate_license(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create first
    res1 = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert res1.status_code == 201
    
    # Create second with same license
    res2 = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert res2.status_code == 409
    assert "Duplicate license number" in res2.json()["detail"]

# 2. Expired license validation
def test_create_driver_expired_license(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    payload = valid_driver_payload.copy()
    payload["license_expiry_date"] = (date.today() - timedelta(days=1)).isoformat()
    
    response = client.post("/api/v1/drivers/", json=payload, headers=headers)
    # Registration with expired license should return 409 Conflict
    assert response.status_code == 409
    assert "License has expired" in response.json()["detail"]

def test_create_driver_expired_available_fails(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    payload = valid_driver_payload.copy()
    payload["license_expiry_date"] = (date.today() - timedelta(days=5)).isoformat()
    payload["status"] = "AVAILABLE"
    
    response = client.post("/api/v1/drivers/", json=payload, headers=headers)
    # Should still trigger 409 Conflict because of expired license validation precedence
    assert response.status_code == 409

# 3. Update driver
def test_update_driver_success(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    # Create first
    create_res = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert create_res.status_code == 201
    driver_id = create_res.json()["id"]
    
    # Update safety_score and contact_number
    update_payload = {
        "safety_score": 95,
        "contact_number": "9876543210"
    }
    update_res = client.put(f"/api/v1/drivers/{driver_id}", json=update_payload, headers=headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["safety_score"] == 95
    assert data["contact_number"] == "9876543210"

def test_update_driver_duplicate_license(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    # Create driver A
    res_a = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert res_a.status_code == 201
    
    # Create driver B
    payload_b = valid_driver_payload.copy()
    payload_b["license_number"] = f"LIC-{uuid.uuid4().hex[:8].upper()}"
    res_b = client.post("/api/v1/drivers/", json=payload_b, headers=headers)
    assert res_b.status_code == 201
    driver_b_id = res_b.json()["id"]
    
    # Try to update B's license to A's license
    update_payload = {
        "license_number": valid_driver_payload["license_number"]
    }
    response = client.put(f"/api/v1/drivers/{driver_b_id}", json=update_payload, headers=headers)
    assert response.status_code == 409
    assert "Duplicate license number" in response.json()["detail"]

# 4. Delete driver
def test_delete_driver_success(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    create_res = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert create_res.status_code == 201
    driver_id = create_res.json()["id"]
    
    # Delete
    delete_res = client.delete(f"/api/v1/drivers/{driver_id}", headers=headers)
    assert delete_res.status_code == 204
    
    # Get verify
    get_res = client.get(f"/api/v1/drivers/{driver_id}", headers=headers)
    assert get_res.status_code == 404

def test_delete_driver_on_trip_fails(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    payload = valid_driver_payload.copy()
    payload["status"] = "ON_TRIP"
    create_res = client.post("/api/v1/drivers/", json=payload, headers=headers)
    assert create_res.status_code == 201
    driver_id = create_res.json()["id"]
    
    # Try Delete
    delete_res = client.delete(f"/api/v1/drivers/{driver_id}", headers=headers)
    assert delete_res.status_code == 409
    assert "Cannot delete driver because status is ON_TRIP" in delete_res.json()["detail"]

# 5. Filters (status, category, expired, safety score)
def test_filter_drivers(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    # Create driver A (HMV, AVAILABLE, safety=90)
    payload_a = valid_driver_payload.copy()
    payload_a["license_number"] = f"LIC-{uuid.uuid4().hex[:8].upper()}"
    payload_a["license_category"] = "HMV"
    payload_a["status"] = "AVAILABLE"
    payload_a["safety_score"] = 90
    res_a = client.post("/api/v1/drivers/", json=payload_a, headers=headers)
    assert res_a.status_code == 201
    
    # Create driver B (LMV, SUSPENDED, safety=60)
    payload_b = valid_driver_payload.copy()
    payload_b["license_number"] = f"LIC-{uuid.uuid4().hex[:8].upper()}"
    payload_b["license_category"] = "LMV"
    payload_b["status"] = "SUSPENDED"
    payload_b["safety_score"] = 60
    res_b = client.post("/api/v1/drivers/", json=payload_b, headers=headers)
    assert res_b.status_code == 201
    
    # Filter by status
    res_status = client.get("/api/v1/drivers/?status=SUSPENDED&limit=100", headers=headers)
    assert res_status.status_code == 200
    assert any(x["license_number"] == payload_b["license_number"] for x in res_status.json()["items"])
    assert not any(x["license_number"] == payload_a["license_number"] for x in res_status.json()["items"])
    
    # Filter by license category
    res_cat = client.get("/api/v1/drivers/?license_category=HMV&limit=100", headers=headers)
    assert res_cat.status_code == 200
    assert any(x["license_number"] == payload_a["license_number"] for x in res_cat.json()["items"])
    assert not any(x["license_number"] == payload_b["license_number"] for x in res_cat.json()["items"])

    # Filter by safety score min
    res_safety = client.get("/api/v1/drivers/?safety_score_min=75&limit=100", headers=headers)
    assert res_safety.status_code == 200
    assert any(x["license_number"] == payload_a["license_number"] for x in res_safety.json()["items"])
    assert not any(x["license_number"] == payload_b["license_number"] for x in res_safety.json()["items"])

# 6. Search
def test_search_drivers(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    
    import random
    payload = valid_driver_payload.copy()
    unique_id = uuid.uuid4().hex[:6]
    payload["license_number"] = f"LIC-{unique_id}"
    payload["full_name"] = f"Alex Rodriguez {unique_id}"
    payload["contact_number"] = "".join(random.choices("0123456789", k=12))
    client.post("/api/v1/drivers/", json=payload, headers=headers)
    
    # Search by full name
    res1 = client.get(f"/api/v1/drivers/?search=Alex Rodriguez {unique_id}", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["total"] == 1

# 7. Pagination
def test_pagination_drivers(tokens):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/drivers/?page=1&limit=2", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "page" in data
    assert "limit" in data
    assert "total" in data
    assert data["page"] == 1
    assert data["limit"] == 2

# 8. Sorting
def test_sorting_drivers(tokens):
    headers = {"Authorization": f"Bearer {tokens['Fleet Manager']}"}
    response = client.get("/api/v1/drivers/?sort_by=safety_score&order=desc", headers=headers)
    assert response.status_code == 200
    items = response.json()["items"]
    if len(items) >= 2:
        assert items[0]["safety_score"] >= items[1]["safety_score"]

# 9. Unauthorized access
def test_unauthorized_access_drivers():
    response = client.get("/api/v1/drivers/")
    assert response.status_code == 401
    
    headers = {"Authorization": "Bearer invalidjwttoken"}
    response2 = client.get("/api/v1/drivers/", headers=headers)
    assert response2.status_code == 401

# 10. Forbidden RBAC access (Driver role)
def test_forbidden_rbac_access_driver_role(tokens, valid_driver_payload):
    headers = {"Authorization": f"Bearer {tokens['Driver']}"}
    
    # Read access forbidden
    res_get = client.get("/api/v1/drivers/", headers=headers)
    assert res_get.status_code == 403
    
    # Write access forbidden
    res_post = client.post("/api/v1/drivers/", json=valid_driver_payload, headers=headers)
    assert res_post.status_code == 403
