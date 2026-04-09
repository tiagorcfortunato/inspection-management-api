"""
app — Inspection Management API

A production-grade, AI-powered REST API for managing road infrastructure
inspections. Inspectors submit damage reports with photos, and the system
autonomously classifies damage type and severity using computer vision.

Architecture (layered, top-down):

    Routers  →  Services  →  Models / Schemas  →  Core
    (HTTP)      (Logic)      (DB / Validation)    (Auth, Config, Enums)

    ┌────────────┐
    │  Routers   │  Handle HTTP requests, validate input, return responses
    └─────┬──────┘
          ▼
    ┌────────────┐
    │  Services  │  Business logic, AI orchestration, DB operations
    └─────┬──────┘
          ▼
    ┌────────────┐  ┌────────────┐
    │   Models   │  │  Schemas   │  ORM entities / Pydantic validation
    └─────┬──────┘  └────────────┘
          ▼
    ┌────────────┐
    │    Core    │  Auth, config, enums, rate limiting
    └────────────┘

Key design decisions:
- AI classification runs as a BackgroundTask (non-blocking)
- Groq SDK used directly for vision; LangChain for text-only structured output
- Human-in-the-loop: AI override tracking when users change AI decisions
"""
