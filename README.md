# Inspection Management API

A backend REST API for managing infrastructure inspections — road damage reports, severity classification, status tracking, filtering, pagination, and sorting.

Built to demonstrate a clean, production-oriented backend architecture using FastAPI, SQLAlchemy, PostgreSQL, Alembic, Docker, and a thorough automated test suite.

## Tech Stack

- **Python** + **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Alembic** — database migrations
- **Docker** — containerised execution
- **Pytest** — 31 automated tests covering auth, CRUD, filtering, pagination, sorting, validation, and admin access control

## Features

### Authentication
- User registration and login
- JWT-based authentication
- Protected routes via dependency injection

### Inspection Management
- Create, retrieve, update, and delete inspection records
- Status lifecycle: `reported` → `verified` → `scheduled` → `repaired`
- Each user only has access to their own inspections

### Filtering
- Filter by `severity`, `status`, and `damage_type`

### Pagination
- `limit` and `offset` query parameters

### Sorting
- Sort by `reported_at`, `severity`, or `status`
- `asc` or `desc` order

## API Endpoints

### Auth
```
POST /auth/register
POST /auth/login
```

### Inspections
```
GET    /inspections
POST   /inspections
GET    /inspections/{inspection_id}
PUT    /inspections/{inspection_id}
DELETE /inspections/{inspection_id}
```

### Example Queries
```
GET /inspections?severity=high
GET /inspections?status=reported
GET /inspections?damage_type=pothole
GET /inspections?limit=10&offset=0
GET /inspections?sort_by=reported_at&order=desc
```

## Project Structure

```
inspection-management-api/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── enums.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── inspection.py
│   │   └── user.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── inspections.py
│   │   └── users.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   └── inspection.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   └── inspection_service.py
│   │
│   ├── database.py
│   └── main.py
│
├── tests/
│   └── test_api.py
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
├── alembic.ini
└── README.md
```

## Architecture

The project follows a layered architecture where each layer has a single responsibility:

| Layer | Responsibility |
|---|---|
| **Routers** | Handle HTTP requests and responses |
| **Services** | Contain business logic |
| **Models** | Define database entities |
| **Schemas** | Validate request and response data |
| **Core** | Centralise auth, dependencies, and enums |

## Local Development

### 1. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/taskdb
SECRET_KEY=your-secret-key-here
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
alembic upgrade head
```

### 4. Run the API

```bash
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`
Swagger docs at `http://localhost:8000/docs`

## Running with Docker

```bash
docker compose up --build
```

## Testing

```bash
# Run tests
docker compose run tests

# Run tests with coverage
docker compose run tests pytest --cov=app
```

## Database Migrations

```bash
# Apply migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "migration message"
```

## Live Demo

The API is deployed and accessible at:

- **API:** https://inspection-management-api.onrender.com
- **Swagger docs:** https://inspection-management-api.onrender.com/docs
- **Frontend dashboard:** https://inspection-dashboard.vercel.app

## Author

Tiago Fortunato
