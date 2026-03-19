#!/bin/sh
set -e

alembic stamp f1d210e1fe25
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000