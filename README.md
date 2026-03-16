# Task Management API

FastAPI backend for a task management system with authentication and PostgreSQL.

## Tech Stack

FastAPI  
PostgreSQL  
SQLAlchemy  
Alembic  
Docker  
Pytest  

## Features

User registration and login (JWT)  
Task CRUD  
User task isolation  
Database migrations  
Automated tests  

## Run locally

docker compose up --build

API:
http://localhost:8000/docs

## Run tests

docker compose run tests

## Test coverage

docker compose run tests pytest --cov=app
