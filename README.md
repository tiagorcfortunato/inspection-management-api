# Inspection Management API

![CI](https://github.com/tiagorcfortunato/inspection-management-api/actions/workflows/ci.yml/badge.svg)

A full-stack, AI-powered road inspection management system. Inspectors report road damage with photos — the AI autonomously classifies damage type and severity using computer vision, while keeping humans in the loop with override tracking and explainable decisions.

**Live demo:** https://inspection-dashboard.vercel.app
**API docs:** https://inspection-management-api.onrender.com/docs

---

## Table of Contents

- [Why This Project](#why-this-project)
- [System Architecture](#system-architecture)
- [AI Pipeline — How It Works](#ai-pipeline--how-it-works)
- [Human-in-the-Loop: AI Override Tracking](#human-in-the-loop-ai-override-tracking)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Key Design Decisions](#key-design-decisions)
- [Local Development](#local-development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Future Improvements](#future-improvements)

---

## Why This Project

Road inspection is manual, slow, and inconsistent. Different inspectors classify the same damage differently. This system solves that by:

1. **Automating classification** — AI analyzes uploaded photos and classifies damage type + severity
2. **Keeping humans in control** — inspectors can override AI decisions, and overrides are tracked
3. **Providing transparency** — every AI decision includes a rationale explaining *why* it classified the way it did (Explainable AI)

---

## System Architecture

```
┌─────────────────────┐         ┌──────────────────────────────┐
│   Frontend (Vercel)  │  HTTPS  │     Backend API (Render)      │
│   Vanilla JS + CSS   │◄───────►│     FastAPI + SQLAlchemy      │
│                      │         │                                │
│  • Dashboard         │         │  ┌──────────┐  ┌───────────┐  │
│  • Create/Edit forms │         │  │  Routers  │  │  Services  │  │
│  • AI status polling │         │  │  (HTTP)   │──│ (Business) │  │
│  • Override warnings │         │  └──────────┘  └─────┬─────┘  │
└─────────────────────┘         │                       │        │
                                │  ┌──────────┐  ┌──────┴─────┐  │
                                │  │  Models   │  │ AI Service │  │
                                │  │  (ORM)    │  │  (Groq SDK)│  │
                                │  └─────┬────┘  └──────┬─────┘  │
                                │        │              │        │
                                └────────┼──────────────┼────────┘
                                         │              │
                                ┌────────▼────┐  ┌──────▼───────┐
                                │ PostgreSQL   │  │  Groq Cloud   │
                                │ (Render DB)  │  │  LLaMA 4 Scout│
                                └─────────────┘  │  Vision Model  │
                                                  └───────────────┘
```

### Request Flow

1. **Frontend** (Vercel) sends requests to the **Backend API** (Render)
2. Backend handles auth, validation, and CRUD via **FastAPI routers**
3. Business logic lives in **services** (separated from HTTP layer)
4. **Models** define the database schema, **schemas** validate API contracts
5. AI classification happens **asynchronously** via background tasks

---

## AI Pipeline — How It Works

When an inspector creates a new inspection (with a photo and/or notes), the AI pipeline runs autonomously:

```
User submits inspection with photo
         │
         ▼
┌─────────────────────┐
│ POST /inspections    │──► Returns 201 immediately (no waiting)
└─────────┬───────────┘
          │
          ▼ (Background Task)
┌─────────────────────────────────────────────┐
│ 1. Compress image (resize to 1024px, JPEG)  │
│ 2. Send to Groq LLaMA 4 Scout vision model │
│ 3. Parse JSON response                      │
│ 4. Update DB: damage_type, severity,        │
│    ai_rationale, ai_damage_type,            │
│    ai_severity, is_ai_processed = true      │
└─────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│ Frontend polls GET /inspections/{id}        │
│ every 3 seconds until is_ai_processed=true  │
│ Then displays "AI Verified" + rationale     │
└─────────────────────────────────────────────┘
```

### Why Background Tasks?

The AI call takes 2-5 seconds. Instead of making the user wait, the API returns instantly and processes the image in the background. The frontend polls for the result — the user sees "AI Analyzing..." that automatically updates to "AI Verified" when done.

### Why Groq SDK Directly (Not LangChain)?

LangChain's `ChatGroq` wrapper doesn't properly forward image content to Groq's API. For **vision** (image + text), the code uses the **Groq SDK directly** (`AsyncGroq`). For **text-only** classification (notes without images), it uses **LangChain with structured output** — which enforces type-safe enum values via function calling.

### Image Compression

Before sending to the AI, images are automatically compressed:
- Resized to max **1024px** on the longest side
- Converted to **JPEG at 75% quality**
- This keeps the payload within Groq's API limits without losing classification accuracy

### Explainable AI (XAI)

Every AI classification includes a `rationale` — a single sentence explaining the decision. This is stored in `ai_rationale` and displayed in the dashboard, so inspectors can understand *why* the AI classified the way it did, rather than treating it as a black box.

---

## Human-in-the-Loop: AI Override Tracking

The AI assists but doesn't have the final say. When a human inspector disagrees with the AI:

```
┌───────────────────────────────────────────────────┐
│ AI classifies: Crack / High severity              │
│                                                    │
│ Inspector edits → changes to: Pothole / Medium     │
│                                                    │
│ ┌───────────────────────────────────────────────┐  │
│ │ ⚠️ Warning: You are overriding AI             │  │
│ │ classification: Crack / High                   │  │
│ └───────────────────────────────────────────────┘  │
│                                                    │
│ After save:                                        │
│ • Badge changes from "AI Verified" → "AI Overridden"│
│ • Original AI classification preserved in DB        │
│ • Override is visible to admins and managers         │
└───────────────────────────────────────────────────┘
```

### How It's Implemented

| Field | Purpose |
|---|---|
| `damage_type` / `severity` | Current values (editable by user) |
| `ai_damage_type` / `ai_severity` | Original AI classification (immutable) |
| `is_ai_processed` | Whether AI has run |
| `is_ai_overridden` | Computed: `true` when current values differ from AI values |

The `is_ai_overridden` is a **hybrid property** on the SQLAlchemy model — computed on read, not stored — so it's always accurate.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Web Framework** | FastAPI | Async support, dependency injection, auto-generated OpenAPI docs |
| **ORM** | SQLAlchemy | Mature, flexible, supports hybrid properties |
| **Database** | PostgreSQL | Production-grade relational DB |
| **Migrations** | Alembic | Version-controlled schema changes |
| **AI (Vision)** | Groq SDK + LLaMA 4 Scout | Fast inference, vision model for image classification |
| **AI (Text)** | LangChain + ChatGroq | Structured output for type-safe text classification |
| **Image Processing** | Pillow | Compress/resize before AI processing |
| **Auth** | JWT (python-jose) + bcrypt | Stateless authentication |
| **Rate Limiting** | SlowAPI | Protect against abuse |
| **Frontend** | Vanilla JS + CSS | Lightweight, no framework overhead |
| **Deployment** | Render (API + DB) + Vercel (frontend) | Free tier, auto-deploy from GitHub |
| **CI** | GitHub Actions | Automated testing on every push |
| **Containerization** | Docker + Docker Compose | Consistent local development |

---

## Features

### Authentication & Authorization
- User registration and login with JWT tokens
- Password hashing with bcrypt
- Role-based access: **user** vs **admin**
- Admin endpoints for cross-user inspection management
- Rate limiting on auth endpoints

### Inspection CRUD
- Create inspections with location, damage type, severity, notes, and photos
- Status lifecycle: `reported` → `verified` → `scheduled` → `repaired`
- Users can only access their own inspections
- Admins can view and manage all inspections

### AI-Powered Classification
- Autonomous image classification via Groq vision model
- Text-based classification from inspector notes
- Background processing with real-time status polling
- Explainable rationale for every AI decision
- Override tracking when humans disagree with AI

### Filtering, Pagination & Sorting
- Filter by `severity`, `status`, `damage_type`
- Paginate with `limit` and `offset`
- Sort by `reported_at`, `severity`, `status`, `damage_type`, `location_code`
- Ascending or descending order

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive JWT token |

### Inspections (User)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/inspections` | List user's inspections (with filters) |
| `POST` | `/inspections` | Create inspection (triggers AI) |
| `GET` | `/inspections/{id}` | Get single inspection |
| `PUT` | `/inspections/{id}` | Update inspection |
| `DELETE` | `/inspections/{id}` | Delete inspection |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/inspections` | List all users' inspections |
| `PUT` | `/admin/inspections/{id}` | Update any inspection |
| `DELETE` | `/admin/inspections/{id}` | Delete any inspection |

### Query Examples
```
GET /inspections?severity=high&status=reported
GET /inspections?damage_type=pothole&limit=5&offset=10
GET /inspections?sort_by=severity&order=desc
```

---

## Project Structure

```
inspection-management-api/
│
├── alembic/                          # Database migrations
│   └── versions/
│       ├── cb036a6df90a_initial_schema.py
│       ├── f3a9b2c1d4e5_add_role_to_users.py
│       ├── 8b7c1a2d9e3f_add_ai_fields.py
│       ├── c4e2f1a8b3d6_add_image_data.py
│       └── d5f3a7b9c2e1_add_ai_override_tracking.py
│
├── app/
│   ├── core/
│   │   ├── config.py                 # Pydantic settings (env vars)
│   │   ├── deps.py                   # FastAPI dependencies (auth, DB)
│   │   ├── enums.py                  # DamageType, Severity, Status enums
│   │   ├── limiter.py                # Rate limiting config
│   │   └── security.py               # JWT token creation & validation
│   │
│   ├── models/
│   │   ├── inspection.py             # Inspection ORM model + is_ai_overridden
│   │   └── user.py                   # User ORM model
│   │
│   ├── routers/
│   │   ├── auth.py                   # Registration & login endpoints
│   │   ├── inspections.py            # User inspection CRUD
│   │   ├── admin.py                  # Admin inspection management
│   │   └── users.py                  # User profile
│   │
│   ├── schemas/
│   │   ├── auth.py                   # Auth request/response schemas
│   │   └── inspection.py             # Inspection request/response schemas
│   │
│   ├── services/
│   │   ├── ai_service.py             # Groq vision + LangChain text AI
│   │   ├── auth_service.py           # Registration & login logic
│   │   └── inspection_service.py     # CRUD + background AI processing
│   │
│   ├── database.py                   # SQLAlchemy engine & session
│   └── main.py                       # FastAPI app, middleware, routers
│
├── tests/
│   └── test_api.py                   # 31 automated tests
│
├── .github/workflows/ci.yml          # GitHub Actions CI pipeline
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

### Layered Architecture

| Layer | Files | Responsibility |
|---|---|---|
| **Routers** | `routers/*.py` | HTTP request/response handling, status codes |
| **Services** | `services/*.py` | Business logic, AI orchestration, DB operations |
| **Models** | `models/*.py` | Database entities, computed properties |
| **Schemas** | `schemas/*.py` | API contract validation (Pydantic) |
| **Core** | `core/*.py` | Cross-cutting: auth, config, enums, rate limiting |

Each layer only depends on the layer below it. Routers never touch the database directly — they go through services.

---

## Database Schema

```
┌──────────────────────────────────────────────┐
│                  users                        │
├──────────────────────────────────────────────┤
│ id           │ INTEGER PK                     │
│ email        │ VARCHAR (unique)               │
│ password     │ VARCHAR (bcrypt hash)          │
│ role         │ VARCHAR (user / admin)         │
│ created_at   │ TIMESTAMP                      │
└──────────┬───────────────────────────────────┘
           │ 1:N
┌──────────▼───────────────────────────────────┐
│                inspections                    │
├──────────────────────────────────────────────┤
│ id              │ INTEGER PK                  │
│ location_code   │ VARCHAR                     │
│ damage_type     │ VARCHAR (current value)     │
│ severity        │ VARCHAR (current value)     │
│ status          │ VARCHAR (lifecycle state)   │
│ notes           │ VARCHAR                     │
│ image_data      │ TEXT (base64)               │
│ ai_rationale    │ VARCHAR (XAI explanation)   │
│ ai_damage_type  │ VARCHAR (original AI value) │
│ ai_severity     │ VARCHAR (original AI value) │
│ is_ai_processed │ BOOLEAN                     │
│ reported_at     │ TIMESTAMP                   │
│ user_id         │ INTEGER FK → users.id       │
└──────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Background Tasks over Synchronous AI Calls
**Problem:** AI classification takes 2-5 seconds. Making the user wait blocks the UX.
**Solution:** Return `201` immediately, process AI in a `BackgroundTask`, frontend polls until done.
**Trade-off:** Added complexity (polling, status tracking) but much better user experience.

### 2. Groq SDK for Vision, LangChain for Text
**Problem:** LangChain's `ChatGroq` wrapper doesn't forward image content to Groq's API.
**Solution:** Use the native `groq.AsyncGroq` client for vision requests (JSON parsing), LangChain's `.with_structured_output()` for text-only (type-safe enums).
**Trade-off:** Two code paths, but each uses the best tool for the job.

### 3. Storing AI Classification Separately
**Problem:** If AI writes directly to `damage_type`/`severity` and the user edits them, we lose what the AI originally said.
**Solution:** Store AI results in `ai_damage_type`/`ai_severity` alongside the editable fields. Compute `is_ai_overridden` as a hybrid property.
**Trade-off:** Extra columns, but enables override tracking without any data loss.

### 4. Image Compression Before AI
**Problem:** High-resolution photos can be several MB, exceeding API limits.
**Solution:** Automatically resize to max 1024px and compress to JPEG 75% using Pillow before sending to Groq.
**Trade-off:** Slight quality loss, but no impact on classification accuracy.

### 5. Hybrid Property for Override Detection
**Problem:** Need `is_ai_overridden` in API responses without storing a redundant boolean.
**Solution:** SQLAlchemy `@hybrid_property` computes it on read by comparing current vs AI fields.
**Trade-off:** Computed on every read, but avoids stale data — always accurate.

---

## Local Development

### 1. Set up environment variables

```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/taskdb
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
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

API at `http://localhost:8000` | Swagger docs at `http://localhost:8000/docs`

### Running with Docker

```bash
docker compose up --build
```

---

## Testing

```bash
# Run tests
docker compose run tests

# Run with coverage
docker compose run tests pytest --cov=app
```

31 automated tests covering:
- Authentication (register, login, JWT validation)
- CRUD operations (create, read, update, delete)
- Filtering by severity, status, damage type
- Pagination and sorting
- Input validation and error handling
- Admin access control and role enforcement

---

## Deployment

| Component | Platform | Auto-deploy |
|---|---|---|
| **API** | Render (Web Service) | On push to `main` |
| **Database** | Render (PostgreSQL) | Managed |
| **Frontend** | Vercel | On push to `main` |

Both repos deploy automatically when code is pushed to `main`. Render runs migrations on deploy via the build command.

---

## Future Improvements

- **AI Confidence Score** — return confidence level so low-confidence items get flagged for human review
- **Audit Trail** — track all changes: who created, who edited, who overrode AI, with timestamps
- **Analytics Dashboard** — damage type distribution, severity trends, AI vs human agreement rate
- **Batch AI Retry** — admin button to re-process all stuck "AI Analyzing..." inspections
- **Image URL Storage** — store images in cloud storage (S3) instead of base64 in the database
- **WebSocket Updates** — replace polling with real-time push notifications when AI finishes

---

## Author

**Tiago Fortunato**
- GitHub: [@tiagorcfortunato](https://github.com/tiagorcfortunato)
