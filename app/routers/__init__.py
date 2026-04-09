"""
app.routers — HTTP Endpoint Definitions

FastAPI routers that handle HTTP requests and delegate to services.
Routers are responsible for request validation, authentication enforcement,
and HTTP status codes — but never contain business logic directly.

    auth.py           Registration and login (with rate limiting)
    inspections.py    User-scoped inspection CRUD + AI background task trigger
    admin.py          Admin-only cross-user inspection management
    users.py          Current user profile endpoint
"""
