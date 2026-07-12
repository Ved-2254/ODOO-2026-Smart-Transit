# Authentication Status - TransitOps Backend

This document details the completed implementation of the production-ready Authentication and Authorization module for the TransitOps FastAPI backend.

---

## 1. Completed Features

- **Password Cryptography**: Reusable password hashing and verification using the industrial-standard `bcrypt` library directly, preventing deprecation/compatibility runtime issues with legacy libraries.
- **JWT Authorization**: Creation and decoding of JWT Access Tokens, utilizing `python-jose`. Claims include: `user_id`, `email`, `role`, and expiration (`exp`).
- **User Registration**: `POST /api/auth/register` validates uniqueness of the email address, enforces a minimum 8-character password length constraint, checks that the specified role exists, hashes the password, and stores the user.
- **User Login**: `POST /api/auth/login` validates credentials against the database and returns a signed JWT access token along with the user info block.
- **Current User Dependency**: A robust, reusable dependency `get_current_user()` that reads the Bearer token, decodes/verifies the signature and expiration, retrieves the user from the database (e.gager loading user roles via SQLAlchemy joined load), and handles missing or invalid authentication credentials by returning a standard `401 Unauthorized` response.
- **Protected Endpoint**: `GET /api/auth/me` retrieves the current logged-in user profile, requiring authentication.
- **Database Seeding**: Automatic seeding of default system roles (`Fleet Manager`, `Dispatcher`, `Safety Officer`, `Financial Analyst`, `Driver`, `Admin`) in the lifespan startup hook.
- **Interactive API Documentation**: Full configuration for Swagger UI, enabling the "Authorize" button for global Bearer authentication.

---

## 2. Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Registers a new user. Validates role and unique email. | No |
| `POST` | `/api/auth/login` | Authenticates email/password and returns a JWT access token. | No |
| `GET` | `/api/auth/me` | Returns the profile of the currently logged-in user. | Yes (Bearer Token) |

---

## 3. Folder Structure

```text
backend/app/
├── api/
│   ├── auth.py              # Auth routes router (register, login, me)
│   └── deps.py              # Shared database session dependencies
├── core/
│   ├── config.py            # System configuration & env loading
│   ├── dependencies.py      # Auth-specific dependencies (get_current_user)
│   └── security.py          # Cryptographic hashing & JWT utilities
├── db/
│   ├── database.py          # SQLAlchemy engine, session, base mixins
│   └── seed.py              # Default database roles seeding routine
├── models/
│   ├── role.py              # Role database model
│   └── user.py              # User database model
├── schemas/
│   └── auth.py              # Pydantic validation & response schemas
└── services/
    └── auth_service.py      # DB operations and user services
```

---

## 4. Example Requests

### A. Register User (`POST /api/auth/register`)
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "name": "Jane Doe",
  "email": "jane.doe@transitops.com",
  "password": "securepassword123",
  "role": "Fleet Manager"
}
```

### B. Login User (`POST /api/auth/login`)
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "email": "jane.doe@transitops.com",
  "password": "securepassword123"
}
```

### C. Get Current User Profile (`GET /api/auth/me`)
- **Headers**:
  - `Authorization: Bearer <YOUR_ACCESS_TOKEN_HERE>`

---

## 5. Example Responses

### A. Register User (`201 Created`)
```json
{
  "id": "2ba37a4b-9705-4c0b-af86-63e020478051",
  "name": "Jane Doe",
  "email": "jane.doe@transitops.com",
  "role": "Fleet Manager"
}
```

### B. Login User (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMmJhMzdhNGItOTcwNS00YzBiLWFmODYtNjNlMDIwNDc4MDUxIiwiZW1haWwiOiJqYW5lLmRvZUB0cmFuc2l0b3BzLmNvbSIsInJvbGUiOiJGbGVldCBNYW5hZ2VyIiwiZXhwIjoxNzg5MTg2MzQwfQ...",
  "token_type": "bearer",
  "user": {
    "id": "2ba37a4b-9705-4c0b-af86-63e020478051",
    "name": "Jane Doe",
    "email": "jane.doe@transitops.com",
    "role": "Fleet Manager"
  }
}
```

### C. Get Current User Profile (`200 OK`)
```json
{
  "id": "2ba37a4b-9705-4c0b-af86-63e020478051",
  "name": "Jane Doe",
  "email": "jane.doe@transitops.com",
  "role": "Fleet Manager"
}
```

### D. Error Responses
- **Email already registered / Role does not exist (`400 Bad Request`)**:
```json
{
  "detail": "Email already registered"
}
```
- **Invalid login credentials / Expired token (`401 Unauthorized`)**:
```json
{
  "detail": "Incorrect email or password"
}
```

---

## 6. Required Environment Variables

Ensure these variables are set in your `.env` file at `backend/.env`:

```env
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<dbname>
SECRET_KEY=temporary-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=11520
```

---

## 7. Testing Instructions

### Automated Tests
Run the comprehensive test suite locally using the following command inside the `backend` directory:
```powershell
.\venv\Scripts\python -m pytest app/tests/test_auth.py -v
```

### Manual Testing in Swagger
1. Start the FastAPI development server:
   ```powershell
   .\venv\Scripts\uvicorn app.main:app --reload
   ```
2. Navigate to `http://127.0.0.1:8000/docs`.
3. Locate the **Authorize** lock button in the top right.
4. Test `/api/auth/register` using a fresh email payload.
5. Test `/api/auth/login` to obtain the token.
6. Copy the `access_token` value from the login response, click the **Authorize** button, paste the token, and click **Authorize**.
7. Run the GET request on `/api/auth/me` to verify it successfully retrieves the profile.

---

## 8. Known Assumptions

- **Deleted Users**: Users are physically persistent in the PostgreSQL database. If a user is manually soft-deleted or marked as inactive by setting the `is_active` boolean column to `False`, the JWT token validation dependency will reject authentication with a `401 Unauthorized` exception.
- **Roles Seeding**: Default standard roles are automatically verified and seeded on application startup. If they are already seeded, the startup function acts as a no-op to avoid database churn.
