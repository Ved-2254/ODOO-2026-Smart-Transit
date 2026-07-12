# Automated Test Results - TransitOps Backend Modules

This document outlines the test results for the Authentication, JWT Authorization, Role-Based Access Control (RBAC), and Vehicle Management modules of the TransitOps FastAPI backend.

---

## 1. Test Suite Configuration

- **Testing Tool**: `pytest-9.1.1`
- **Client implementation**: FastAPI `TestClient` (utilizing `httpx`)
- **Execution Command**:
  ```powershell
  .\venv\Scripts\python -m pytest app/tests/ -v
  ```
- **Total Test Cases**: 30 Cases
- **Outcome**: **30 Passed / 0 Failed (100% Success)**

---

## 2. Tested Cases & Outcomes

### Authentication & Token Validation (`app/tests/test_auth.py`)

| # | Test Case Name | Objective | Checked Status | Outcome |
|---|---|---|---|---|
| 1 | `test_register_success` | Create user with valid email, name, role. | `201 Created` | **PASSED** |
| 2 | `test_register_duplicate_email` | Block register if email is already taken. | `400 Bad Request` | **PASSED** |
| 3 | `test_register_invalid_role` | Block register if the role does not exist in the db. | `400 Bad Request` | **PASSED** |
| 4 | `test_register_password_too_short` | Enforce minimum 8-character password constraint via Pydantic model. | `422 Unprocessable` | **PASSED** |
| 5 | `test_login_success` | Return token and user block for valid email and password. | `200 OK` | **PASSED** |
| 6 | `test_login_invalid_credentials` | Block login for incorrect password. | `401 Unauthorized` | **PASSED** |
| 7 | `test_get_me_success` | Return current user details for valid token. | `200 OK` | **PASSED** |
| 8 | `test_get_me_unauthorized` | Block current user extraction if auth header is missing or malformed. | `401 Unauthorized` | **PASSED** |
| 9 | `test_get_me_expired_token` | Block access for a signature-valid token that has expired. | `401 Unauthorized` | **PASSED** |

### Role-Based Access Control (`app/tests/test_rbac.py`)

| # | Test Case Name | Objective | Checked Status | Outcome |
|---|---|---|---|---|
| 10 | `test_get_vehicles_authorized_roles` | Allow `Fleet Manager` and `Admin` to read vehicles. | `200 OK` | **PASSED** |
| 11 | `test_get_vehicles_unauthorized_roles` | Block `Driver` from reading vehicles. | `403 Forbidden` | **PASSED** |
| 12 | `test_post_vehicles_authorized_roles` | Allow `Fleet Manager` and `Admin` to create vehicles. | `201 Created` | **PASSED** |
| 13 | `test_post_vehicles_unauthorized_roles` | Block `Driver` from creating vehicles. | `403 Forbidden` | **PASSED** |
| 14 | `test_get_drivers_authorized_roles` | Allow `Safety Officer`, `Fleet Manager`, and `Admin` to read drivers list. | `200 OK` | **PASSED** |
| 15 | `test_get_drivers_unauthorized_roles` | Block `Financial Analyst` from reading drivers list. | `403 Forbidden` | **PASSED** |
| 16 | `test_get_expenses_authorized_roles` | Allow `Financial Analyst` and `Admin` to view expenses. | `200 OK` | **PASSED** |
| 17 | `test_get_expenses_unauthorized_roles` | Block `Fleet Manager` from viewing expenses. | `403 Forbidden` | **PASSED** |

### Vehicle Management (`app/tests/test_vehicles.py`)

| # | Test Case Name | Objective | Checked Status | Outcome |
|---|---|---|---|---|
| 18 | `test_create_vehicle_success` | Create vehicle with valid payload (Fleet Manager/Admin). | `201 Created` | **PASSED** |
| 19 | `test_create_vehicle_duplicate_registration` | Block duplicate registration numbers. | `409 Conflict` | **PASSED** |
| 20 | `test_update_vehicle_success` | Allow updating vehicle fields (Fleet Manager/Admin). | `200 OK` | **PASSED** |
| 21 | `test_update_vehicle_duplicate_registration` | Block updating registration to one already used by another vehicle. | `409 Conflict` | **PASSED** |
| 22 | `test_delete_vehicle_success` | Successfully delete an existing vehicle (Fleet Manager/Admin). | `204 No Content` | **PASSED** |
| 23 | `test_delete_vehicle_on_trip_fails` | Block deletion of vehicles with status `ON_TRIP`. | `409 Conflict` | **PASSED** |
| 24 | `test_filter_vehicles` | Filter vehicles list by status and type query parameters. | `200 OK` | **PASSED** |
| 25 | `test_search_vehicles` | Search vehicles matching registration, name, and model. | `200 OK` | **PASSED** |
| 26 | `test_pagination_vehicles` | Support page and limit query parameters for listing. | `200 OK` | **PASSED** |
| 27 | `test_sorting_vehicles` | Support sort_by and order (asc/desc) query parameters. | `200 OK` | **PASSED** |
| 28 | `test_unauthorized_access` | Block access to vehicles API when JWT token is missing/invalid. | `401 Unauthorized` | **PASSED** |
| 29 | `test_forbidden_rbac_access_driver` | Block Drivers from accessing vehicles API entirely. | `403 Forbidden` | **PASSED** |
| 30 | `test_read_only_roles_forbidden_write` | Safety Officer/Financial Analyst can read, but blocked from writing. | `403/200 OK` | **PASSED** |

---

## 3. Command Execution Console Log Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0 -- D:\PROJECTS\ODOO-2026\backend\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\PROJECTS\ODOO-2026\backend
plugins: anyio-4.14.1
collecting ... collected 30 items

app/tests/test_auth.py::test_register_success PASSED                     [  3%]
app/tests/test_auth.py::test_register_duplicate_email PASSED             [  6%]
app/tests/test_auth.py::test_register_invalid_role PASSED                [ 10%]
app/tests/test_auth.py::test_register_password_too_short PASSED          [ 13%]
app/tests/test_auth.py::test_login_success PASSED                        [ 16%]
app/tests/test_auth.py::test_login_invalid_credentials PASSED            [ 20%]
app/tests/test_auth.py::test_get_me_success PASSED                       [ 23%]
app/tests/test_auth.py::test_get_me_unauthorized PASSED                  [ 26%]
app/tests/test_auth.py::test_get_me_expired_token PASSED                 [ 30%]
app/tests/test_rbac.py::test_get_vehicles_authorized_roles PASSED        [ 33%]
app/tests/test_rbac.py::test_get_vehicles_unauthorized_roles PASSED      [ 36%]
app/tests/test_rbac.py::test_post_vehicles_authorized_roles PASSED       [ 40%]
app/tests/test_rbac.py::test_post_vehicles_unauthorized_roles PASSED     [ 43%]
app/tests/test_rbac.py::test_get_drivers_authorized_roles PASSED         [ 46%]
app/tests/test_rbac.py::test_get_drivers_unauthorized_roles PASSED       [ 50%]
app/tests/test_rbac.py::test_get_expenses_authorized_roles PASSED        [ 53%]
app/tests/test_rbac.py::test_get_expenses_unauthorized_roles PASSED      [ 56%]
app/tests/test_vehicles.py::test_create_vehicle_success PASSED           [ 60%]
app/tests/test_vehicles.py::test_create_vehicle_duplicate_registration PASSED [ 63%]
app/tests/test_vehicles.py::test_update_vehicle_success PASSED           [ 66%]
app/tests/test_vehicles.py::test_update_vehicle_duplicate_registration PASSED [ 70%]
app/tests/test_vehicles.py::test_delete_vehicle_success PASSED           [ 73%]
app/tests/test_vehicles.py::test_delete_vehicle_on_trip_fails PASSED     [ 76%]
app/tests/test_vehicles.py::test_filter_vehicles PASSED                  [ 80%]
app/tests/test_vehicles.py::test_search_vehicles PASSED                  [ 83%]
app/tests/test_vehicles.py::test_pagination_vehicles PASSED              [ 86%]
app/tests/test_vehicles.py::test_sorting_vehicles PASSED                 [ 90%]
app/tests/test_vehicles.py::test_unauthorized_access PASSED              [ 93%]
app/tests/test_vehicles.py::test_forbidden_rbac_access_driver PASSED     [ 96%]
app/tests/test_vehicles.py::test_read_only_roles_forbidden_write PASSED  [100%]

============================== warnings summary ===============================
venv\Lib\site-packages\fastapi\testclient.py:1
  D:\PROJECTS\ODOO-2026\backend\venv\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 30 passed in 202.58s =======================
```
