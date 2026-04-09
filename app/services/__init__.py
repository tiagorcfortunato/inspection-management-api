"""
app.services — Business Logic Layer

All domain logic lives here. Services are called by routers and interact
with models and external APIs. Routers never access the database directly.

    ai_service.py           Multimodal AI classification via Groq (vision + text)
    auth_service.py         User registration, login, and admin role assignment
    inspection_service.py   Inspection CRUD, filtering/sorting, and async AI processing

Key design decision: AI classification runs as a FastAPI BackgroundTask,
dispatched from the create endpoint. The service creates its own DB session
for the background task since the request session is already closed.
"""
