# Inspection Management API

A backend service built with FastAPI for managing infrastructure inspections such as road damage reports, severity classification, status tracking, filtering, pagination, and sorting.

This project demonstrates a clean backend architecture using FastAPI, SQLAlchemy, PostgreSQL, Alembic migrations, Docker, and automated API tests.

## Overview

The API allows authenticated users to manage inspection records in a structured way.
It simulates a backend service that could be used by municipalities, infrastructure maintenance teams, or inspection platforms.

Main capabilities include:

- user registration and login
- protected endpoints with JWT authentication
- inspection creation, update, retrieval, and deletion
- filtering by severity, status, and damage type
- pagination using limit and offset
- sorting support
- database migrations with Alembic
- containerized execution with Docker
- automated testing with pytest

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Docker
- Pytest

## Project Structure

inspection-management-api/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── core/
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
│   │   └── inspections.py
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

## Features

Authentication

- user registration
- user login with JWT
- protected routes

Inspection Management

- create inspection reports
- retrieve inspections
- retrieve inspection by id
- update inspection fields
- delete inspection records

Filtering

- severity
- status
- damage type

Pagination

- limit
- offset

Sorting

- sort_by
- order

## API Endpoints

Auth

POST /auth/register  
POST /auth/login

Inspections

GET /inspections  
POST /inspections  
GET /inspections/{inspection_id}  
PUT /inspections/{inspection_id}  
DELETE /inspections/{inspection_id}

## Example Query Parameters

Examples using GET /inspections:

/inspections?severity=high  
/inspections?status=reported  
/inspections?damage_type=pothole  
/inspections?limit=10&offset=0  
/inspections?sort_by=reported_at&order=desc

## Local Development

Install dependencies

pip install -r requirements.txt

Run the API

uvicorn app.main:app --reload

API available at

http://localhost:8000

Swagger documentation

http://localhost:8000/docs

## Running with Docker

Build and run containers

docker compose up --build

## Testing

Run tests

docker compose run tests

Run tests with coverage

docker compose run tests pytest --cov=app

## Database Migrations

Apply migrations

alembic upgrade head

Create migration

alembic revision --autogenerate -m "migration message"

## Deployment

After deployment the API will be accessible via:

DEPLOY_URL_HERE

Swagger documentation

DEPLOY_SWAGGER_URL_HERE

These links will be updated once the API is deployed so recruiters can access the live service.

## Architecture

The project follows a layered backend architecture:

routers  
handle HTTP requests and responses

services  
contain business logic

models  
define database entities

schemas  
validate request and response data

core  
centralizes authentication, dependencies, and enums

This separation improves maintainability and scalability.

## Author

Tiago Fortunato