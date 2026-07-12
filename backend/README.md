# TransitOps Backend

Modular, production-ready FastAPI backend for the TransitOps application.

## Prerequisites

- Python 3.12+
- PostgreSQL (or alternative database engine configured in `.env`)

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs.
- **Uvicorn**: Lightning-fast ASGI server implementation.
- **SQLAlchemy**: SQL toolkit and Object Relational Mapper (ORM).
- **Alembic**: Database migrations management.
- **Pydantic**: Data validation and settings management.

## Project Structure

```text
backend/
│
├── alembic/                  # Database migrations folder
├── app/
│   ├── api/                  # API endpoints and dependency injections
│   │   ├── routes/           # Router modules (endpoints)
│   │   └── deps.py           # Dependency injection helpers (e.g. get_db)
│   │
│   ├── core/                 # Core settings, security, and configurations
│   │   ├── config.py         # Pydantic BaseSettings config parsing
│   │   └── security.py       # Password and token utilities
│   │
│   ├── db/                   # Database engine, session, and base definitions
│   │   ├── base.py           # Base model registry for Alembic migrations
│   │   └── database.py       # Database connection initialization
│   │
│   ├── models/               # SQLAlchemy models (entities)
│   ├── schemas/              # Pydantic validation schemas
│   ├── services/             # Core business logic services
│   ├── utils/                # Utility helpers
│   ├── main.py               # Application entrypoint
│   │
│   └── __init__.py
│
├── requirements.txt          # Project dependencies
├── .env.example              # Configuration environment template
└── README.md                 # Project documentation
```

## Getting Started

### 1. Set Up Virtual Environment

```bash
# Navigate to the backend folder
cd backend

# Create virtual environment (if not already done)
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configurations

Copy the `.env.example` file to `.env` and fill in your database credentials:

```bash
cp .env.example .env
```

### 4. Run database migrations

```bash
alembic upgrade head
```

### 5. Start the Development Server

To start the FastAPI server locally:

```bash
uvicorn app.main:app --reload
```

The application will be running at `http://127.0.0.1:8000`.

- Access documentation (Swagger UI) at: `http://127.0.0.1:8000/docs`
- Access status endpoint at: `http://127.0.0.1:8000/` which returns `{"status": "Backend Running"}`
